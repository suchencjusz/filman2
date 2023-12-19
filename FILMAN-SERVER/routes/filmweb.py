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


@filmweb_router.get("/get/movie", response_model=schemas.FilmWebMovie)
async def get_movie(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    movie = crud.get_movie_filmweb_id(db, id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
