from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings

db_url = settings.sqlalchemy_database_url
if settings.is_sqlite:
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
else:
    connect_args = {"connect_timeout": 10}
    pool_kwargs = {"poolclass": NullPool} if settings.is_vercel else {}
    engine = create_engine(db_url, connect_args=connect_args, **pool_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
