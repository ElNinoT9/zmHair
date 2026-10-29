from sqlalchemy import text

from app.config import settings
from app.database import engine

TIME_PERIODS = {
    'morning': '上午',
    'afternoon': '下午',
    'evening': '晚上',
}

DEFAULT_TIME_PERIOD = 'morning'
VALID_TIME_PERIODS = set(TIME_PERIODS.keys())


def time_period_text(value: str) -> str:
    if not value:
        return ''
    return TIME_PERIODS.get(value, value)


def run_migrations():
    if not settings.is_sqlite:
        return

    with engine.begin() as conn:
        appointment_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(appointments)'))}
        if 'time_period' not in appointment_cols:
            conn.execute(text(
                "ALTER TABLE appointments ADD COLUMN time_period VARCHAR(16) NOT NULL DEFAULT ''"
            ))

        user_cols = {row[1] for row in conn.execute(text('PRAGMA table_info(users)'))}
        if 'last_time_period' not in user_cols:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN last_time_period VARCHAR(16) NOT NULL DEFAULT 'morning'"
            ))
