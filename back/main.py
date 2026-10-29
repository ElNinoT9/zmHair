"""
企业内部理发预约系统 - 启动入口

启动后访问:
  - API 文档: http://127.0.0.1:8001/docs
  - 健康检查: http://127.0.0.1:8001/health
"""

from contextlib import asynccontextmanager
import logging
import threading

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.database_migrate import run_migrations
from app.init_data import seed_database
from app.routers import api_router
from app.utils.response import ApiException

logger = logging.getLogger(__name__)


def _run_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception:
        logger.exception('seed_database failed')
    finally:
        db.close()


def _vercel_bootstrap():
    try:
        Base.metadata.create_all(bind=engine)
        run_migrations()
        _run_seed()
    except Exception:
        logger.exception('vercel bootstrap failed')


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_vercel and settings.is_sqlite:
        raise RuntimeError(
            'Vercel 上 SQLite 无法持久化，请在 Vercel 环境变量中设置 DATABASE_URL（PostgreSQL，如 Neon）'
        )
    if settings.is_vercel:
        threading.Thread(target=_vercel_bootstrap, daemon=True).start()
    else:
        Base.metadata.create_all(bind=engine)
        run_migrations()
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    description='企业内部理发预约管理系统 API',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router)


@app.exception_handler(ApiException)
async def api_exception_handler(request, exc: ApiException):
    return JSONResponse(status_code=200, content={'code': exc.code, 'message': exc.message})


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'app': settings.app_name,
        'storage': {
            'engine': settings.storage_engine,
            'persistent': settings.storage_persistent,
            'note': settings.storage_note,
        },
    }


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
