import uvicorn
import ujson


from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from movie import Movie, MovieManager
from watched import WatchedManager
from users import UserManager
from discord_m import DiscordManager
from tasks import TasksManager


app = FastAPI()

from pydantic import BaseModel
from typing import List, Optional


class Movie(BaseModel):
    movie_id: str
    rate: str
    comment: Optional[str] = None
    favourite: bool
    unix_timestamp: str


class MoviesIn(BaseModel):
    id_filmweb: str
    movies: List[Movie]
    without_discord: Optional[bool] = False


class UserIn(BaseModel):
    id_filmweb: str
    id_discord: Optional[int] = None


class MovieIn(BaseModel):
    id_filmweb: str
    movie_id: int
    rate: int
    comment: str
    favourite: bool
    unix_timestamp: int


class MovieUpdateIn(BaseModel):
    id: int
    title: str
    year: int
    poster_url: str
    community_rate: float


class DiscordUserIdIn(BaseModel):
    id_discord: int


class TaskUpdate(BaseModel):
    type: str
    status: str


class TaskUpdateIn(BaseModel):
    id_task: int
    status: str


class GuildIn(BaseModel):
    id_filmweb: str
    id_guild: int


class GuildStopIn(BaseModel):
    id_discord: int
    guild_id: int


class GuildConfigureIn(BaseModel):
    guild_id: int
    channel_id: int


##################################################
# USER
##################################################


@app.get("/user/watched/film/all")
async def get_all_movies(id_filmweb: str):
    watched_manager = WatchedManager()
    result = watched_manager.get_all_watched_movies(id_filmweb)
    if result is None:
        raise HTTPException(status_code=500, detail="No movies found")
    else:
        return result


class MovieWatched(BaseModel):
    id_watched: int
    id_filmweb: str
    movie_id: int
    rate: int
    comment: str
    favourite: bool
    unix_timestamp: int

class MovieWatchedList(BaseModel):
    id_filmweb: str
    movies: List[MovieWatched]
    without_discord: Optional[bool] = False


@app.post("/user/watched/film/add_many")
async def add_many_movies(movies_in: MovieWatchedList):
    watched_manager = WatchedManager()

    for movie in movies_in.movies:
        watched_manager.add_watched_movie(
            movies_in.id_filmweb,
            movie.movie_id,
            movie.rate,
            movie.comment,
            movie.favourite,
            movie.unix_timestamp,
            movies_in.without_discord,
        )

    return {"message": "OK"}


@app.post("/user/create")
async def create_user(user_in: UserIn):
    user_manager = UserManager()
    result = user_manager.create_user(user_in.id_filmweb, user_in.id_discord)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.post("/user/watched/film/add")
async def add_movie(movie_in: MovieIn):
    watched_manager = WatchedManager()
    result = watched_manager.add_watched_movie(
        movie_in.id_filmweb,
        movie_in.movie_id,
        movie_in.rate,
        movie_in.comment,
        movie_in.favourite,
        movie_in.unix_timestamp,
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


##################################################
# MOVIE
##################################################


@app.post("/movie/update")
async def update_movie(movie_update_in: MovieUpdateIn):
    movie_manager = MovieManager()

    result = movie_manager.add_movie_to_db(
        Movie(
            id=movie_update_in.id,
            title=movie_update_in.title,
            year=movie_update_in.year,
            poster_uri=movie_update_in.poster_url,
            community_rate=movie_update_in.community_rate,
        )
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


##################################################
# TASKS
##################################################


@app.get("/tasks/get")
async def get_tasks(status: str = None, type: str = None):
    tasks_manager = TasksManager()
    result = tasks_manager.get_and_update_tasks(type, status)
    if result is None:
        raise HTTPException(status_code=500, detail="No tasks found")
    else:
        return result


# tak to sa dwie inne funkcje
@app.get("/task/get")
async def get_task(type: str = None):
    tasks_manager = TasksManager()
    result = tasks_manager.get_task_by_type(type)
    if result is None:
        raise HTTPException(status_code=500, detail="No tasks found")
    else:
        return result


@app.get("/task/update")
async def update_task(id_task: int, status: str):
    tasks_manager = TasksManager()
    result = tasks_manager.update_task_status(id_task, status)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


##################################################
# DISCORD
##################################################


@app.post("/discord/user/stop")
async def stop_user_notifications(guild_stop_in: GuildStopIn):
    discord_manager = DiscordManager()
    result = discord_manager.delete_user_from_guild(
        guild_stop_in.id_discord, guild_stop_in.guild_id
    )
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.post("/discord/user/cancel")
async def cancel_user_notifications(discord_user_id: DiscordUserIdIn):
    discord_manager = DiscordManager()
    result = discord_manager.delete_user_from_all_destinations(
        discord_user_id.id_discord
    )
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.post("/discord/user/add")
async def add_user_to_guild(guild_in: GuildIn):
    discord_manager = DiscordManager()
    result = discord_manager.add_user_to_guild(guild_in.id_filmweb, guild_in.id_guild)
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.post("/discord/configure/guild")
async def configure_guild(guild_configure_in: GuildConfigureIn):
    discord_manager = DiscordManager()
    result = discord_manager.configure_guild(
        guild_configure_in.guild_id, guild_configure_in.channel_id
    )
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
