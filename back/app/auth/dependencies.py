from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.models.models import User
from app.utils.response import ApiException


def _get_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith('Bearer '):
        raise ApiException(401, '请先登录')
    return authorization[7:]


def get_current_user(
    token: str = Depends(_get_token),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise ApiException(401, '请先登录')
    user = db.get(User, payload.get('user_id'))
    if not user or not user.is_active:
        raise ApiException(401, '请先登录')
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != 'admin':
        raise ApiException(403, '无管理员权限')
    return current_user
