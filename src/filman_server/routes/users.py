from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from filman_server.database import crud, models, schemas
from filman_server.database.db import SessionLocal, engine, get_db

from typing import Optional, List, Dict, Any

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post("/create", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")


@users_router.get("/get", response_model=schemas.User)
async def get_user(
    id: Optional[int] = None,
    filmweb_id: Optional[str] = None,
    discord_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, id, filmweb_id, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#
# discord guild actions
#


@users_router.get("/add_to_guild", response_model=schemas.DiscordDestinations)
async def add_to_guild(
    discord_user_id: int,
    discord_guild_id: int,
    db: Session = Depends(get_db),
):
    user_id = crud.get_user(db, id=None, filmweb_id=None, discord_id=discord_user_id)

    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user_id.id

    guild = crud.get_guild(db, discord_guild_id)

    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")

    discord_destination = crud.set_user_destination(db, user_id=user_id, discord_guild_id=discord_guild_id)

    return discord_destination


@users_router.get("/remove_from_guild", response_model=schemas.DiscordDestinations)
async def remove_from_guild(
    user_id: int,
    discord_guild_id: int,
    db: Session = Depends(get_db),
):
    guild = crud.get_guild(db, discord_guild_id)
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")

    discord_destination = crud.get_user_destinations(db, user_id)
    if discord_destination is None:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    discord_destination = crud.get_user_destination(db, user_id, discord_guild_id)
    if discord_destination is None:
        raise HTTPException(status_code=404, detail="User not found in this guild")

    crud.delete_user_destination(db, user_id, discord_guild_id)

    return discord_destination


@users_router.get("/remove_from_all_guilds", response_model=schemas.DiscordDestinations)
async def remove_from_all_guilds(
    user_id: int,
    db: Session = Depends(get_db),
):
    discord_destination = crud.get_user_destinations(db, user_id)
    if discord_destination is None:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    crud.delete_discord_destinations(db, user_id)

    return discord_destination
