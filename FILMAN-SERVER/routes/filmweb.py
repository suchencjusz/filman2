from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import crud, models, schemas
from database.db import SessionLocal, engine

from typing import Optional, List, Dict, Any

filmweb_router = APIRouter(prefix="/filmweb", tags=["filmweb"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
# MOVIES
#
        

@filmweb_router.get("/get/movie", response_model=schemas.FilmWebMovie)
async def get_movie(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    movie = crud.get_movie_filmweb_id(db, id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@filmweb_router.post("/add/movie", response_model=schemas.FilmWebMovie)
async def add_movie(
    movie: schemas.FilmWebMovieCreate,
    db: Session = Depends(get_db),
):
    try:
        db_movie = crud.create_filmweb_movie(db, movie)
        return db_movie
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Movie already exists")


@filmweb_router.post("/update/movie", response_model=schemas.FilmWebMovie)
async def update_movie(
    movie: schemas.FilmWebMovie,
    db: Session = Depends(get_db),
):
    try:
        db_movie = crud.update_filmweb_movie(db, movie)
        return db_movie
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Movie already exists")

#
# MOVIES WATCHED
#


@filmweb_router.post(
    "/watched/movies/add", response_model=schemas.FilmWebUserWatchedMovieCreate
)
async def add_watched_movie(
    user_watched_movie: schemas.FilmWebUserWatchedMovieCreate,
    db: Session = Depends(get_db),
):
    try:
        db_movie = crud.create_filmweb_user_watched_movie(db, user_watched_movie)

        # tu sie powinien tworzyc task do crawlera
        # ze sie musi pobrac film z filmweba i dodac do bazy

        if db_movie is None or db_movie is IntegrityError:
            raise HTTPException(status_code=404, detail="Movie not found")

        return db_movie
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Movie already in user watched")

@filmweb_router.get(
    "/watched/movies/get/ids", response_model=List[int]
)
async def get_watched_movies_ids(
    id: Optional[int] = None,
    filmweb_id: Optional[str] = None,
    discord_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, id, filmweb_id, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    filmweb_id = user.filmweb_id

    watched_movies = crud.get_filmweb_user_watched_movies_ids(db, filmweb_id)

    if watched_movies is None:
        raise HTTPException(status_code=404, detail="User has no watched movies")

    return watched_movies

@filmweb_router.get(
    "/watched/movies/get", response_model=List[schemas.FilmWebUserWatchedMovie]
)
async def get_watched_movies(
    id: Optional[int] = None,
    filmweb_id: Optional[str] = None,
    discord_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, id, filmweb_id, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    filmweb_id = user.filmweb_id

    watched_movies = crud.get_filmweb_user_watched_movies(db, filmweb_id)

    if watched_movies is None:
        raise HTTPException(status_code=404, detail="User has no watched movies")

    print(watched_movies)

    return watched_movies

#
# SERIES
#

@filmweb_router.get("/get/series", response_model=schemas.FilmWebSeries)
async def get_series(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    series = crud.get_series_filmweb_id(db, id)
    if series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return series

@filmweb_router.post("/add/series", response_model=schemas.FilmWebSeries)
async def add_series(
    series: schemas.FilmWebSeriesCreate,
    db: Session = Depends(get_db),
):
    try:
        db_series = crud.create_filmweb_series(db, series)
        return db_series
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Series already exists")
    
@filmweb_router.post("/update/series", response_model=schemas.FilmWebSeries)
async def update_series(
    series: schemas.FilmWebSeries,
    db: Session = Depends(get_db),
):
    try:
        db_series = crud.update_filmweb_series(db, series)
        return db_series
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Series already exists")