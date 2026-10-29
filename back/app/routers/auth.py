from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.database import get_db
from app.models.models import User
from app.schemas.common import ChangePasswordRequest, LoginRequest, QuickLoginRequest
from app.services.employee_import import normalize_employee_id
from app.utils.response import ApiException

router = APIRouter(prefix='/auth', tags=['认证'])


def _login_response(user: User):
    token = create_access_token(user)
    return {
        'code': 0,
        'message': '登录成功',
        'data': {'token': token, 'user': user.to_dict()},
    }


@router.post('/login')
def login(body: LoginRequest, db: Session = Depends(get_db)):
    employee_id = normalize_employee_id(body.employee_id) or body.employee_id.strip()
    if not employee_id:
        raise ApiException(400, '请输入工号')

    user = db.query(User).filter_by(employee_id=employee_id).first()
    if not user:
        raise ApiException(404, '工号不存在，请联系管理员')
    if not user.is_active:
        raise ApiException(403, '账号已停用')
    if not user.check_password(body.password):
        raise ApiException(401, '密码错误')

    return _login_response(user)


@router.post('/quick-login')
def quick_login(body: QuickLoginRequest, db: Session = Depends(get_db)):
    """移动端工号快捷登录，无需密码。"""
    employee_id = normalize_employee_id(body.employee_id)
    if not employee_id:
        raise ApiException(400, '请输入工号')

    user = db.query(User).filter_by(employee_id=employee_id).first()
    if not user:
        raise ApiException(404, '工号不存在，请联系管理员')
    if not user.is_active:
        raise ApiException(403, '账号已停用')
    if user.role == 'admin':
        raise ApiException(403, '管理员请使用 PC 后台登录')

    return _login_response(user)


@router.get('/lookup')
def lookup_employee(employee_id: str, db: Session = Depends(get_db)):
    """根据工号查询姓名，用于登录页实时展示。"""
    normalized = normalize_employee_id(employee_id)
    if not normalized:
        return {'code': 0, 'data': None}

    user = db.query(User).filter_by(employee_id=normalized, is_active=True).first()
    if not user or user.role == 'admin':
        return {'code': 0, 'data': None}

    return {'code': 0, 'data': {'employee_id': user.employee_id, 'name': user.name}}


@router.get('/profile')
def profile(current_user: User = Depends(get_current_user)):
    return {'code': 0, 'data': current_user.to_dict()}


@router.post('/change-password')
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.old_password or not body.new_password:
        raise ApiException(400, '请输入原密码和新密码')
    if len(body.new_password) < 4:
        raise ApiException(400, '新密码至少4位')
    if not current_user.check_password(body.old_password):
        raise ApiException(401, '原密码错误')

    current_user.set_password(body.new_password)
    db.commit()
    return {'code': 0, 'message': '密码修改成功'}
