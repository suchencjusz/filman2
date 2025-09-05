import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL", "sqlite:///filman.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
