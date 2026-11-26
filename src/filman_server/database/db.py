import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "sqlite:///filman.db")

_engine_kwargs: dict = {"pool_pre_ping": True}
if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(
        pool_recycle=1800,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        connect_args={
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        },
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

"""Database core objects.

Migration side-effects are intentionally not triggered here to avoid circular
imports (models -> db -> migrate -> models). Use
filman_server.database.migrate.trigger_migrations() after models are imported
at application startup.
"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
