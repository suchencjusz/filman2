from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post(
    "/create",
    response_model=schemas.User,
    summary="Create a user",
    description="Create a user using discord user id",
)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except IntegrityError:
        raise HTTPException(status_code=202, detail="User already exists")


@users_router.get(
    "/get",
    response_model=schemas.User,
    summary="Get a user",
    description="Get a user by user_id, filmweb_id or discord_id",
)
async def get_user(
    user_id: int | None = None,
    filmweb_id: str | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    if user_id is None and filmweb_id is None and discord_id is None:
        raise HTTPException(status_code=400, detail="Either user_id, filmweb_id or discord_id is required")

    user = crud.get_user(db, user_id, filmweb_id, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.get(
    "/get_all",
    response_model=List[schemas.User],
    summary="Get all users",
    description="Get all users",
)
async def get_all_users(
    db: Session = Depends(get_db),
):
    users = crud.get_users(db)
    if users is None:
        raise HTTPException(status_code=404, detail="No users found")
    return users


#
# discord guild actions
#


@users_router.get(
    "/get_all_channels",
    response_model=List[int],
    summary="Get all guild text channels",
    description="Get all discord guild text channels, where notifications can be sent",
)
async def get_channels(
    user_id: int | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user_id, None, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    discord_destinations = crud.get_user_destinations(db, user_id, discord_id)
    if discord_destinations is None or len(discord_destinations) == 0:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    discord_channels = crud.get_user_destinations_channels(db, user_id, discord_id)
    if discord_channels is None or len(discord_channels) == 0:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    return discord_channels


@users_router.get(
    "/get_all_guilds",
    response_model=List[schemas.DiscordDestinations],
    summary="Get all user guilds",
    description="Get all guilds user is in",
)
async def get_guilds(
    user_id: int | None = None,
    discord_id: int | None = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user_id, None, discord_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    discord_destinations = crud.get_user_destinations(db, user_id, discord_id)
    if discord_destinations is None or len(discord_destinations) == 0:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    return discord_destinations


@users_router.get(
    "/add_to_guild",
    response_model=schemas.DiscordDestinations,
    summary="Add user to discord guild",
    description="Add user to discord guild (guild must be in db first)",
)
async def add_to_guild(
    discord_id: int,
    discord_guild_id: int,
    db: Session = Depends(get_db),
):
    user_id = crud.get_user(db, None, None, discord_id)

    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user_id.id

    guild = crud.get_guild(db, discord_guild_id)

    if guild is None:
        raise HTTPException(status_code=405, detail="Guild not found")

    discord_destination = crud.get_user_destination(db, user_id, discord_id, discord_guild_id)
    if discord_destination is not None:
        raise HTTPException(status_code=409, detail="User already in this guild")

    discord_destination = crud.set_user_destination(db, user_id=user_id, discord_guild_id=discord_guild_id)

    return discord_destination


@users_router.delete(
    "/remove_from_guild",
    response_model=schemas.DiscordDestinations,
    summary="Remove user from discord guild",
    description="Remove user from discord (the message destination for notifications)",
)
async def remove_from_guild(
    user_id: int | None = None,
    discord_user_id: int | None = None,
    discord_guild_id: int = None,
    db: Session = Depends(get_db),
):

    if user_id is None and discord_user_id is None:
        raise HTTPException(status_code=400, detail="Either user_id or discord_user_id is required")

    guild = crud.get_guild(db, discord_guild_id)
    if guild is None:
        raise HTTPException(status_code=404, detail="Guild not found")

    discord_destination = crud.get_user_destinations(db, user_id, discord_user_id)
    if discord_destination is None:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    discord_destination = crud.get_user_destination(db, user_id, discord_user_id, discord_guild_id)
    if discord_destination is None:
        raise HTTPException(status_code=404, detail="User not found in this guild")

    crud.delete_user_destination(db, user_id, discord_user_id, discord_guild_id)

    return discord_destination


@users_router.delete(
    "/remove_from_all_guilds",
    response_model=List[schemas.DiscordDestinations],
    summary="Remove user from all guilds",
    description="Remove user from all guilds (the message destinations for notifications)",
)
async def remove_from_all_guilds(
    user_id: int | None = None,
    discord_user_id: int | None = None,
    db: Session = Depends(get_db),
):
    if user_id is None and discord_user_id is None:
        raise HTTPException(status_code=400, detail="Either user_id or discord_user_id is required")

    discord_destinations = crud.get_user_destinations(db, user_id, discord_user_id)
    if discord_destinations is None:
        raise HTTPException(status_code=404, detail="User not found in any guild")

    crud.delete_user_destinations(db, user_id, discord_user_id)

    return discord_destinations
