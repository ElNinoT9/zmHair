import os

from pydantic import model_validator
from pydantic_settings import BaseSettings


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _database_url_from_env() -> str | None:
    """Vercel Postgres / Neon 等常用环境变量名。"""
    for key in (
        "DATABASE_URL",
        "POSTGRES_URL",
        "POSTGRES_URL_NON_POOLING",
        "POSTGRES_PRISMA_URL",
    ):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return None


class Settings(BaseSettings):
    app_name: str = "企业内部理发预约系统"
    secret_key: str = "zmhair-dev-secret-change-in-production"
    jwt_expire_hours: int = 72
    database_url: str = "sqlite:///./zmhair.db"
    host: str = "127.0.0.1"
    port: int = 8001
    reload: bool = True

    class Config:
        env_file = ".env"

    @model_validator(mode="after")
    def apply_cloud_database_url(self):
        """线上优先使用 PostgreSQL 连接串（持久化存储）。"""
        env_url = _database_url_from_env()
        if env_url:
            self.database_url = env_url
        return self

    @property
    def sqlalchemy_database_url(self) -> str:
        return _normalize_database_url(self.database_url)

    @property
    def is_vercel(self) -> bool:
        return bool(os.getenv("VERCEL"))

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")

    @property
    def storage_engine(self) -> str:
        if self.is_sqlite:
            return "sqlite"
        if self.sqlalchemy_database_url.startswith("postgresql"):
            return "postgresql"
        return "other"

    @property
    def storage_persistent(self) -> bool:
        """业务数据是否落在可持久化的数据库上。"""
        if self.is_vercel:
            return not self.is_sqlite
        return True

    @property
    def storage_note(self) -> str:
        if self.is_vercel and self.is_sqlite:
            return "Vercel 无本地磁盘，请配置 DATABASE_URL 或 POSTGRES_URL（PostgreSQL）"
        if self.is_sqlite:
            return "本地 SQLite 文件 zmhair.db，请定期备份"
        return "PostgreSQL 云端持久化，请在控制台开启自动备份"


settings = Settings()
