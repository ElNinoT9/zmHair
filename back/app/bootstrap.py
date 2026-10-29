"""Vercel 上延迟初始化，避免冷启动 30s 超时。"""
import logging
import threading

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.database_migrate import run_migrations
from app.init_data import seed_database

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_ready = False


def ensure_bootstrapped() -> None:
    global _ready
    if _ready:
        return
    with _lock:
        if _ready:
            return
        Base.metadata.create_all(bind=engine)
        run_migrations()
        db = SessionLocal()
        try:
            # Vercel 只做轻量种子（管理员+理发师+配置）；员工库请本机脚本导入 Neon
            seed_database(db, light=settings.is_vercel)
        finally:
            db.close()
        _ready = True
        logger.info("bootstrap complete")
