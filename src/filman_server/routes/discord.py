from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from filman_server.database import crud, models, schemas
from filman_server.database.db import SessionLocal, engine, get_db

discord_router = APIRouter(prefix="/discord", tags=["discord"])


@discord_router.post("/configure/guild", response_model=schemas.DiscordGuilds)
async def configure_guild(guild: schemas.DiscordGuildsCreate, db: Session = Depends(get_db)):
    try:
        db_guild = crud.set_guild(db, guild)
        return db_guild
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Guild already exists")
