import logging
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from filman_server.database import crud, schemas
from filman_server.database.db import get_db

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

discord_router = APIRouter(prefix="/discord", tags=["discord"])


@discord_router.post(
    "/configure/guild",
    response_model=schemas.DiscordGuilds,
    summary="Configure a guild",
    description="Configure a discord guild, this endpoint is connecting a guild text channel to guild id (is used for managing where notifications are sent)",
)
async def configure_guild(
    guild: schemas.DiscordGuildsCreate, db: Session = Depends(get_db)
):
    try:
        db_guild = crud.set_guild(db, guild)
        return db_guild
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Guild already exists")


@discord_router.get(
    "/guilds",
    response_model=List[schemas.DiscordGuilds],
    summary="Get all guilds",
    description="Get all guilds that are configured in the database",
)
async def get_guilds(db: Session = Depends(get_db)):
    guilds = crud.get_guilds(db)
    return guilds


@discord_router.get(
    "/guild/members",
    response_model=List[schemas.User],
    summary="Get all members of provided guild",
    description="Simply returns all members of the provided guild",
)
async def get_guild_members(discord_guild_id: int, db: Session = Depends(get_db)):
    guild_members = crud.get_guild_members(db, discord_guild_id)
    return guild_members
