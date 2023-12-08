import sqlite3
import uvicorn
import mysql.connector
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from movie import Movie, MovieManager
from watched import WatchedManager
from users import UserManager
from discord_m import DiscordManager


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/user/create")
async def create_user(id_filmweb: str, id_discord: int):
    user_manager = UserManager()
    result = user_manager.create_user(id_filmweb, id_discord)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/user/delete")
async def delete_user(id_filmweb: str):
    user_manager = UserManager()
    if user_manager.delete_user(id_filmweb):
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/user/watched/film/add")
async def add_movie(
    id_filmweb: str,
    movie_id: int,
    rate: int,
    comment: str,
    favourite: bool,
    unix_timestamp: int,
):
    watched_manager = WatchedManager()
    result = watched_manager.add_watched_movie(
        id_filmweb, movie_id, rate, comment, favourite, unix_timestamp
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/user/watched/film/all")
async def get_all_watched_movie(id_filmweb: str):
    watched_manager = WatchedManager()
    result = watched_manager.get_all_watched_movie(id_filmweb)
    if result is None:
        raise HTTPException(status_code=500, detail="No movies found")
    else:
        return result


@app.get("/movie/update")
async def update_movie(
    id: int,
    title: str,
    year: int,
    poster_url: str,
    community_rate: float,
):
    movie_manager = MovieManager()

    result = movie_manager.add_movie_to_db(
        Movie(id=id, title=title, year=year, poster_uri=poster_url, community_rate=community_rate)
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


# @app.get("/task/get")
# async def get_task():
#     pass


@app.get("/discord/user/guilds_destinations")
async def get_user_guilds_destinations(id_filmweb: str):
    discord_manager = DiscordManager()
    result = discord_manager.get_user_guilds(id_filmweb)
    if result is None or len(result) == 0:
        raise HTTPException(status_code=500, detail="No guilds found")
    else:
        return result


@app.get("/discord/user/cancel")
async def cancel_user_notifications(id_filmweb: str):
    discord_manager = DiscordManager()
    result = discord_manager.delete_user_from_all_guilds(id_filmweb)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/discord/user/stop")
async def stop_user_notifications(id_filmweb: str, id_guild: int):
    discord_manager = DiscordManager()
    result = discord_manager.delete_user_from_guild(id_filmweb, id_guild)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/discord/user/add")
async def add_user_to_guild(id_filmweb: str, id_guild: int):
    discord_manager = DiscordManager()
    result = discord_manager.add_user_to_guild(id_filmweb, id_guild)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/discord/configure/guild")
async def configure_guild(guild_id: int, channel_id: int):
    discord_manager = DiscordManager()
    result = discord_manager.configure_guild(guild_id, channel_id)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
