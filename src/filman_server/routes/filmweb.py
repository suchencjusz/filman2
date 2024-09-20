from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

filmweb_router = APIRouter(prefix="/filmweb", tags=["filmweb"])


#
# MOVIES
#


@filmweb_router.get(
    "/movie/get",
    response_model=schemas.FilmWebMovie,
    summary="Get movie",
    description="Get movie by id",
)
async def get_movie(
    id: int,
    db: Session = Depends(get_db),
):
    movie = crud.get_movie_filmweb_id(db, id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@filmweb_router.post(
    "/movie/update",
    response_model=schemas.FilmWebMovie,
    summary="Update/insert movie to database",
    description="Updates movie in database if it exists, otherwise inserts it",
)
async def update_movie(
    movie: schemas.FilmWebMovie,
    db: Session = Depends(get_db),
):
    try:
        db_movie = crud.update_filmweb_movie(db, movie)
        return db_movie
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error")


#
# FILMWEB USER MAPPING
#


@filmweb_router.post(
    "/user/mapping/set",
    response_model=schemas.FilmWebUserMapping,
    summary="Set user mapping",
    description="Set user mapping between discord user and filmweb username",
)
async def set_user_mapping(
    user_mapping: schemas.FilmWebUserMappingCreate,
    db: Session = Depends(get_db),
):
    r = requests.get(f"https://www.filmweb.pl/api/v1/user/{user_mapping.filmweb_id}/preview")

    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="Filmweb user not found")

    try:
        db_user_mapping = crud.set_filmweb_user_mapping(db, user_mapping)
        return db_user_mapping
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User mapping already exists")


@filmweb_router.get(
    "/user/mapping/get",
    response_model=schemas.FilmWebUserMapping,
    summary="Get user mapping",
    description="Get user mapping between discord user and filmweb username",
)
async def get_user_mapping(
    user_id: int | None = None,
    filmweb_id: str | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    if user_id is None and filmweb_id is None and discord_id is None:
        raise HTTPException(status_code=400, detail="At least one of user_id, filmweb_id or discord_id must be provided")

    user_mapping = crud.get_filmweb_user_mapping(db, user_id, filmweb_id, discord_id)
    if user_mapping is None:
        raise HTTPException(status_code=404, detail="User mapping not found")
    return user_mapping


@filmweb_router.delete(
    "/user/mapping/delete",
    response_model=bool,
    summary="Delete user mapping",
    description="Delete user mapping between discord user and filmweb username, and watched movies of this user",
)
async def delete_user_mapping(
    user_id: int | None = None,
    filmweb_id: str | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    if user_id is None and filmweb_id is None and discord_id is None:
        raise HTTPException(status_code=400, detail="At least one of user_id, filmweb_id or discord_id must be provided")

    user_mapping = crud.delete_filmweb_user_mapping(db, user_id, discord_id, filmweb_id)

    if user_mapping is None:
        raise HTTPException(status_code=404, detail="User mapping not found")

    if user_mapping is False:
        raise HTTPException(status_code=400, detail="User mapping not deleted")

    return user_mapping


#
# MOVIES WATCHED
#


@filmweb_router.post(
    "/user/watched/movies/add",
    response_model=schemas.FilmWebUserWatchedMovieCreate,
    summary="Add watched movie by user",
    description="Add watched movie by user, if movie does not exist in database it will be added with default values",
)
async def add_watched_movie(
    user_watched_movie: schemas.FilmWebUserWatchedMovieCreate,
    db: Session = Depends(get_db),
):
    try:
        db_movie = crud.create_filmweb_user_watched_movie(db, user_watched_movie)

        # tu sie powinien tworzyc task do crawlera
        # ze sie musi pobrac film z filmweba i dodac do bazy
        # ~2 nie koniecznie

        if db_movie is None or db_movie is IntegrityError:
            raise HTTPException(status_code=404, detail="Movie not found")

        return db_movie
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Movie is already in user watched")


@filmweb_router.get(
    "/user/watched/movies/get_all",
    response_model=List[schemas.FilmWebUserWatchedMovie],
    summary="Get watched movies by user",
    description="Get watched movies by user, with movie details",
)
async def get_watched_movies(
    user_id: int | None = None,
    filmweb_id: str | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    watched_movies = crud.get_filmweb_user_watched_movies(db, user_id, filmweb_id, discord_id)

    if watched_movies is None:
        raise HTTPException(status_code=404, detail="User has no watched movies")

    return watched_movies


@filmweb_router.get(
    "/user/watched/movies/get",
    response_model=schemas.FilmWebUserWatchedMovie,
    summary="Get watched movie by user",
    description="Get watched movie by user, with movie details",
)
async def get_watched_movie(
    user_id: int | None = None,
    filmweb_id: str | None = None,
    discord_id: int | None = None,
    movie_id: int = None,
    db: Session = Depends(get_db),
):
    if user_id is None and filmweb_id is None and discord_id is None:
        raise HTTPException(status_code=400, detail="At least one of user_id, filmweb_id or discord_id must be provided")

    watched_movie = crud.get_filmweb_user_watched_movie(db, user_id, filmweb_id, discord_id, movie_id)

    if watched_movie is None:
        raise HTTPException(status_code=404, detail="User has no watched movies")

    return watched_movie


#
# SERIES
#


# @filmweb_router.get("/get/series", response_model=schemas.FilmWebSeries)
# async def get_series(
#     id: Optional[int] = None,
#     db: Session = Depends(get_db),
# ):
#     series = crud.get_series_filmweb_id(db, id)
#     if series is None:
#         raise HTTPException(status_code=404, detail="Series not found")
#     return series


# @filmweb_router.post("/add/series", response_model=schemas.FilmWebSeries)
# async def add_series(
#     series: schemas.FilmWebSeriesCreate,
#     db: Session = Depends(get_db),
# ):
#     try:
#         db_series = crud.create_filmweb_series(db, series)
#         return db_series
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="Series already exists")


# @filmweb_router.post("/series/update", response_model=schemas.FilmWebSeries)
# async def update_series(
#     series: schemas.FilmWebSeries,
#     db: Session = Depends(get_db),
# ):
#     try:
#         db_series = crud.update_filmweb_series(db, series)
#         return db_series
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="Series already exists")
