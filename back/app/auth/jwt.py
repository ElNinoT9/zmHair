from datetime import datetime, timedelta

import jwt

from app.config import settings


def create_access_token(user) -> str:
    payload = {
        'user_id': user.id,
        'employee_id': user.employee_id,
        'role': user.role,
        'is_barber': user.is_barber,
        'exp': datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.secret_key, algorithm='HS256')


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=['HS256'])
    except jwt.PyJWTError:
        return None
