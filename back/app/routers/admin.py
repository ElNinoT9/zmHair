from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.models import Appointment, SystemConfig, User
from app.schemas.common import ConfigUpdateRequest, UserCreateRequest, UserUpdateRequest
from app.services.employee_import import normalize_employee_id
from app.utils.response import ApiException

router = APIRouter(prefix='/admin', tags=['管理后台'])


@router.get('/users')
def list_users(
    keyword: str = Query(default=''),
    role: str = Query(default=''),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(User)
    if keyword.strip():
        kw = f'%{keyword.strip()}%'
        query = query.filter(or_(User.employee_id.like(kw), User.name.like(kw)))
    if role.strip():
        query = query.filter(User.role == role.strip())

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

    user = User(
        employee_id=employee_id,
        name=name,
        role=body.role,
        is_barber=body.is_barber,
    )
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
        user.role = body.role
    if body.is_barber is not None:
        user.is_barber = body.is_barber
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password:
        user.set_password(body.password)

    db.commit()
    db.refresh(user)
    return {'code': 0, 'message': '更新成功', 'data': user.to_dict()}


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


@router.get('/appointments')
def list_appointments(
    keyword: str = Query(default=''),
    status: str = Query(default=''),
    start_date: str = Query(default=''),
    end_date: str = Query(default=''),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Appointment)
    if keyword.strip():
        kw = f'%{keyword.strip()}%'
        query = query.join(User, Appointment.employee_id == User.id).filter(
            or_(User.name.like(kw), User.employee_id.like(kw))
        )
    if status.strip():
        query = query.filter(Appointment.status == status.strip())
    if start_date.strip():
        query = query.filter(Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date.strip():
        query = query.filter(Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())

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
    status: str = Query(default=''),
    start_date: str = Query(default=''),
    end_date: str = Query(default=''),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(Appointment)
    if status.strip():
        query = query.filter(Appointment.status == status.strip())
    if start_date.strip():
        query = query.filter(Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date.strip():
        query = query.filter(Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())

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
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
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
