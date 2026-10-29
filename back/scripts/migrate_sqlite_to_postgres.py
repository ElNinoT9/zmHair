#!/usr/bin/env python3
"""
将本地 SQLite（zmhair.db）业务数据导入 PostgreSQL（线上持久化库）。

用法（在 back 目录）:
  export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'
  ./venv/bin/python scripts/migrate_sqlite_to_postgres.py

可选:
  SQLITE_PATH=./zmhair.db
  DATABASE_URL 或 POSTGRES_URL
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACK))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import _normalize_database_url
from app.database import Base
from app.models.models import Appointment, BarberSchedule, Notification, SystemConfig, User

SQLITE_PATH = Path(os.getenv("SQLITE_PATH", BACK / "zmhair.db"))


def _target_url() -> str:
    for key in ("DATABASE_URL", "POSTGRES_URL", "POSTGRES_URL_NON_POOLING"):
        val = os.getenv(key, "").strip()
        if val:
            return _normalize_database_url(val)
    print("请设置环境变量 DATABASE_URL（PostgreSQL 连接串）", file=sys.stderr)
    sys.exit(1)


def copy_table(src_session, dst_session, model, label: str):
    rows = src_session.query(model).all()
    for row in rows:
        data = {col.key: getattr(row, col.key) for col in model.__table__.columns}
        dst_session.merge(model(**data))
    dst_session.commit()
    print(f"  {label}: {len(rows)} 条")


def reset_postgres_sequences(engine):
    """PostgreSQL 自增主键与已导入 id 对齐。"""
    tables = ("users", "barber_schedules", "appointments", "notifications", "system_config")
    with engine.begin() as conn:
        for table in tables:
            conn.execute(
                text(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        COALESCE((SELECT MAX(id) FROM {table}), 1)
                    )
                    """
                )
            )


def main():
    if not SQLITE_PATH.exists():
        print(f"未找到 SQLite: {SQLITE_PATH}", file=sys.stderr)
        sys.exit(1)

    target = _target_url()
    if target.startswith("sqlite"):
        print("目标 DATABASE_URL 不能是 SQLite", file=sys.stderr)
        sys.exit(1)

    src_engine = create_engine(f"sqlite:///{SQLITE_PATH.resolve()}")
    dst_engine = create_engine(target)

    print(f"源: {SQLITE_PATH}")
    print(f"目标: PostgreSQL（已隐藏密码）")

    Base.metadata.create_all(bind=dst_engine)

    Src = sessionmaker(bind=src_engine)
    Dst = sessionmaker(bind=dst_engine)
    src = Src()
    dst = Dst()
    try:
        print("导入中…")
        copy_table(src, dst, User, "users")
        copy_table(src, dst, BarberSchedule, "barber_schedules")
        copy_table(src, dst, Appointment, "appointments")
        copy_table(src, dst, Notification, "notifications")
        copy_table(src, dst, SystemConfig, "system_config")
        reset_postgres_sequences(dst_engine)
        print("完成。请访问 /health 确认 storage.persistent 为 true。")
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    main()
