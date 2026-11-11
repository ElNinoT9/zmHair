from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.models import Appointment, BarberSchedule, Notification, SystemConfig, User
from app.schemas.common import ConfigUpdateRequest, UserCreateRequest, UserUpdateRequest
from app.services.employee_import import normalize_employee_id
from app.services.user_roles import VALID_USER_ROLES, apply_role_policy
from app.services.user_excel import (
    build_template_workbook,
    build_users_workbook,
    import_users_from_rows,
    parse_users_from_excel,
)
from app.utils.response import ApiException, content_disposition_attachment

router = APIRouter(prefix='/admin', tags=['管理后台'])


@router.get('/users')
def list_users(
    keyword: str = Query(default=''),
    role: str = Query(default=''),
    is_admin: str = Query(default=''),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(User)
    if keyword.strip():
        kw = f'%{keyword.strip()}%'
        query = query.filter(or_(User.employee_id.like(kw), User.name.like(kw)))
    if role.strip():
        query = query.filter(User.role == role.strip())
    admin_flag = is_admin.strip().lower()
    if admin_flag == 'true':
        query = query.filter(User.role == 'admin')
    elif admin_flag == 'false':
        query = query.filter(User.role != 'admin')

    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        'code': 0,
        'data': {
            'list': [u.to_dict() for u in items],
            'total': total,
            'page': page,
            'page_size': page_size,
        },
    }


@router.post('/users')
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    employee_id = normalize_employee_id(body.employee_id) or body.employee_id.strip()
    name = body.name.strip()
    if not employee_id or not name:
        raise ApiException(400, '工号和姓名不能为空')
    if db.query(User).filter_by(employee_id=employee_id).first():
        raise ApiException(400, '工号已存在')
    role = (body.role or 'employee').strip()
    if role not in VALID_USER_ROLES:
        raise ApiException(400, '无效的角色')
    user = User(
        employee_id=employee_id,
        name=name,
        role=role,
        is_barber=body.is_barber,
    )
    apply_role_policy(user)
    if user.role == 'admin':
        user.is_barber = False
    user.set_password(body.password or employee_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'code': 0, 'message': '创建成功', 'data': user.to_dict()}


@router.put('/users/{user_id}')
def update_user(
    user_id: int,
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise ApiException(404, '用户不存在')

    if body.name is not None:
        user.name = body.name.strip()
    if body.role is not None:
        role = body.role.strip()
        if role not in VALID_USER_ROLES:
            raise ApiException(400, '无效的角色')
        if user.role == 'admin' and role != 'admin':
            raise ApiException(400, '不能修改管理员角色')
        user.role = role
    if body.is_barber is not None:
        user.is_barber = body.is_barber
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password:
        user.set_password(body.password)
    apply_role_policy(user)
    if user.role == 'admin':
        user.is_barber = False

    db.commit()
    db.refresh(user)
    return {'code': 0, 'message': '更新成功', 'data': user.to_dict()}


def _parse_employee_roles(raw: str) -> list[str]:
    allowed = {'employee', 'waixie'}
    roles = [p.strip() for p in (raw or '').split(',') if p.strip()]
    return [r for r in roles if r in allowed]


def _appointments_base_query(
    db: Session,
    *,
    keyword: str,
    status: str,
    start_date: str,
    end_date: str,
    employee_roles: str,
):
    query = db.query(Appointment)
    roles = _parse_employee_roles(employee_roles)
    employee = aliased(User)
    need_employee_join = bool(keyword.strip()) or bool(roles)
    if need_employee_join:
        query = query.join(employee, Appointment.employee_id == employee.id)
        if keyword.strip():
            kw = f'%{keyword.strip()}%'
            query = query.filter(or_(employee.name.like(kw), employee.employee_id.like(kw)))
        if roles:
            query = query.filter(employee.role.in_(roles))
    if status.strip():
        query = query.filter(Appointment.status == status.strip())
    if start_date.strip():
        query = query.filter(Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date.strip():
        query = query.filter(Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    return query


@router.delete('/users/{user_id}')
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise ApiException(404, '用户不存在')
    if user.role == 'admin':
        raise ApiException(400, '不能删除管理员账号')

    user.is_active = False
    db.commit()
    return {'code': 0, 'message': '已停用'}


@router.post('/users/{user_id}/purge')
def purge_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """从数据库永久删除用户（不可恢复）。存在预约记录时不允许删除。"""
    user = db.get(User, user_id)
    if not user:
        raise ApiException(404, '用户不存在')
    if user.role == 'admin':
        raise ApiException(400, '不能删除管理员账号')

    apt_count = (
        db.query(Appointment)
        .filter(or_(Appointment.employee_id == user_id, Appointment.barber_id == user_id))
        .count()
    )
    if apt_count > 0:
        raise ApiException(
            400,
            f'该用户关联 {apt_count} 条预约记录，无法永久删除，请使用「停用」',
        )

    db.query(BarberSchedule).filter_by(barber_id=user_id).delete()
    db.query(Notification).filter_by(user_id=user_id).delete()
    db.delete(user)
    db.commit()
    return {'code': 0, 'message': '用户已永久删除'}


def _users_export_query(db: Session, keyword: str, role: str):
    query = db.query(User)
    if keyword.strip():
        kw = f'%{keyword.strip()}%'
        query = query.filter(or_(User.employee_id.like(kw), User.name.like(kw)))
    if role.strip():
        query = query.filter(User.role == role.strip())
    return query.order_by(User.id.desc())


@router.get('/users/export')
def export_users(
    keyword: str = Query(default=''),
    role: str = Query(default=''),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = _users_export_query(db, keyword, role).all()
    output = build_users_workbook(users)
    filename = f'用户列表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': content_disposition_attachment(filename, 'users_export.xlsx')},
    )


@router.get('/users/import-template')
def download_user_import_template(_: User = Depends(require_admin)):
    output = build_template_workbook()
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': content_disposition_attachment('用户导入模板.xlsx', 'user_import_template.xlsx')
        },
    )


@router.post('/users/import')
async def import_users(
    mode: str = Query(default='update', description='update=更新(默认), overwrite=覆盖'),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if mode not in ('update', 'overwrite'):
        raise ApiException(400, 'mode 须为 update 或 overwrite')
    filename = (file.filename or '').lower()
    if not filename.endswith(('.xlsx', '.xlsm')):
        raise ApiException(400, '请上传 .xlsx 格式的 Excel 文件')

    content = await file.read()
    if not content:
        raise ApiException(400, '文件为空')

    rows, parse_errors = parse_users_from_excel(content)
    if not rows:
        msg = parse_errors[0] if parse_errors else '未解析到有效数据，请使用系统「下载模板」并填写「工号」「姓名」列'
        raise ApiException(400, msg)

    try:
        result = import_users_from_rows(db, rows, mode)
    except Exception as exc:
        db.rollback()
        raise ApiException(500, f'导入失败：{exc}') from exc
    result.errors.extend(parse_errors)

    return {
        'code': 0,
        'message': '导入完成',
        'data': result.to_dict(),
    }


@router.get('/appointments')
def list_appointments(
    keyword: str = Query(default=''),
    status: str = Query(default=''),
    start_date: str = Query(default=''),
    end_date: str = Query(default=''),
    employee_roles: str = Query(default='employee'),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = _appointments_base_query(
        db,
        keyword=keyword,
        status=status,
        start_date=start_date,
        end_date=end_date,
        employee_roles=employee_roles,
    )

    total = query.count()
    items = (
        query.order_by(Appointment.appointment_date.desc(), Appointment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        'code': 0,
        'data': {
            'list': [a.to_dict() for a in items],
            'total': total,
            'page': page,
            'page_size': page_size,
        },
    }


@router.get('/appointments/export')
def export_appointments(
    keyword: str = Query(default=''),
    status: str = Query(default=''),
    start_date: str = Query(default=''),
    end_date: str = Query(default=''),
    employee_roles: str = Query(default='employee'),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = _appointments_base_query(
        db,
        keyword=keyword,
        status=status,
        start_date=start_date,
        end_date=end_date,
        employee_roles=employee_roles,
    )

    appointments = query.order_by(Appointment.appointment_date.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = '预约台账'
    ws.append(['序号', '预约人工号', '预约人姓名', '理发师', '预约日期', '安排时段', '状态', '备注', '创建时间'])
    for idx, apt in enumerate(appointments, 1):
        info = apt.to_dict()
        ws.append([
            idx,
            apt.employee.employee_id if apt.employee else '',
            apt.employee.name if apt.employee else '',
            apt.barber.name if apt.barber else '',
            apt.appointment_date.strftime('%Y-%m-%d'),
            info['time_period_text'],
            info['status_text'],
            apt.remark,
            apt.created_at.strftime('%Y-%m-%d %H:%M:%S') if apt.created_at else '',
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f'预约台账_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': content_disposition_attachment(filename, 'appointments_export.xlsx')},
    )


@router.get('/config')
def get_config(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    configs = db.query(SystemConfig).all()
    return {'code': 0, 'data': [c.to_dict() for c in configs]}


@router.put('/config')
def update_config(
    body: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    for item in body.configs:
        key = item.get('config_key')
        value = item.get('config_value')
        if not key:
            continue
        config = db.query(SystemConfig).filter_by(config_key=key).first()
        if config:
            config.config_value = str(value)
        else:
            db.add(SystemConfig(config_key=key, config_value=str(value)))
    db.commit()
    return {'code': 0, 'message': '配置已保存'}


@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    today = datetime.now().date()
    return {
        'code': 0,
        'data': {
            'total_users': db.query(User).filter_by(is_active=True).count(),
            'total_barbers': db.query(User).filter_by(is_barber=True, is_active=True).count(),
            'total_appointments': db.query(Appointment).count(),
            'pending_appointments': db.query(Appointment).filter_by(status='pending').count(),
            'today_appointments': db.query(Appointment).filter_by(appointment_date=today).count(),
        },
    }
