import json
import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.models import User

SEED_FILE = Path(__file__).resolve().parent.parent.parent / 'data' / 'employees_seed.json'


def normalize_employee_id(raw: str) -> str:
    raw = (raw or '').strip().upper()
    if raw.startswith('CLM'):
        raw = raw[3:]
    digits = re.sub(r'\D', '', raw)
    if not digits:
        return ''
    if len(digits) < 6:
        digits = digits.zfill(6)
    return digits


def extract_employee_id_from_row(row: dict) -> str:
    code = row.get('人员编码') or row.get('employee_id') or ''
    return normalize_employee_id(str(code))


def seed_employees_from_zmhr(db: Session) -> int:
    if not SEED_FILE.exists():
        return 0

    payload = json.loads(SEED_FILE.read_text(encoding='utf-8'))
    rows = payload.get('rows', [])
    count = 0

    for row in rows:
        if row.get('在职状态') and row.get('在职状态') != '在职':
            continue
        name = (row.get('姓名') or '').strip()
        employee_id = extract_employee_id_from_row(row)
        if not name or not employee_id:
            continue

        user = db.query(User).filter_by(employee_id=employee_id).first()
        if user:
            user.name = name
            if user.role == 'employee' and not user.is_barber:
                user.is_active = True
        else:
            user = User(employee_id=employee_id, name=name, role='employee')
            user.set_password(employee_id)
            db.add(user)
        count += 1

    return count
