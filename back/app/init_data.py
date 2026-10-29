from sqlalchemy.orm import Session

from app.models.models import SystemConfig, User
from app.services.employee_import import seed_employees_from_zmhr

# 默认理发师（工号为纯数字，不含 CLM 前缀）
DEFAULT_BARBERS = [
    ('094164', '贾艳争'),
    ('094165', '张岳骁'),
    ('094026', '骆春晖'),
]


def seed_barbers(db: Session):
    for employee_id, name in DEFAULT_BARBERS:
        user = db.query(User).filter_by(employee_id=employee_id).first()
        if user:
            user.name = name
            user.is_barber = True
            user.is_active = True
        else:
            user = User(employee_id=employee_id, name=name, role='employee', is_barber=True)
            user.set_password(employee_id)
            db.add(user)

    legacy = db.query(User).filter_by(employee_id='barber001').first()
    if legacy:
        legacy.is_barber = False


def seed_database(db: Session):
    if not db.query(User).filter_by(role='admin').first():
        admin = User(employee_id='admin', name='系统管理员', role='admin')
        admin.set_password('admin123')
        db.add(admin)

    default_configs = [
        ('system_name', '企业内部理发预约系统', '系统名称'),
        ('schedule_min_days', '7', '理发师排班最少提前天数'),
        ('schedule_max_days', '14', '理发师排班最多提前天数'),
        ('company_name', '公司名称', '公司名称'),
    ]
    for key, value, desc in default_configs:
        if not db.query(SystemConfig).filter_by(config_key=key).first():
            db.add(SystemConfig(config_key=key, config_value=value, description=desc))

    if db.query(User).filter(User.role == 'employee').count() == 0:
        seed_employees_from_zmhr(db)
    seed_barbers(db)

    db.commit()
