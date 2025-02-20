import logging
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

utils_router = APIRouter(prefix="/utils", tags=["utils"])


@utils_router.get(
    "/database_info",
    response_model=schemas.DatabaseInfo,
    summary="Get database info",
    description="Get database info, count of users, mappings, guilds and tasks",
)
def get_database_info(db: Session = Depends(get_db)):
    users_count = len(crud.get_users(db))
    filmweb_watched_movies = len(crud.get_filmweb_watched_movies_all(db))
    filmweb_watched_series = len(crud.get_filmweb_watched_series_all(db))
    guilds_count = len(crud.get_guilds(db))

    return schemas.DatabaseInfo(
        users_count=users_count,
        filmweb_watched_movies=filmweb_watched_movies,
        filmweb_watched_series=filmweb_watched_series,
        discord_guilds=guilds_count,
    )
