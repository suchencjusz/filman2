import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL", "mysql://y168:1B00_3267ae@mysql.mikr.us/db_y168"
)

# SQLALCHEMY_DATABASE_URL = os.environ.get(
#    "SQLALCHEMY_DATABASE_URL", "mysql://root@localhost/filmweb_test3"
# )

print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
