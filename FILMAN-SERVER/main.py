import threading
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List, Optional

from movie import Movie as MovieManagerMovie
from movie import MovieManager

from series import Series as SeriesManagerSeries
from series import SeriesManager

from watched import WatchedManager
from users import UserManager
from discord_m import DiscordManager
from tasks import TasksManager


app = FastAPI()

##################################################
# MODELS
##################################################


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
    poster_uri: str
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
    id_discord: int
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
    id_watched: Optional[int] = None
    id_filmweb: str
    movie_id: int
    rate: int
    comment: Optional[str] = None
    favorite: bool = False
    unix_timestamp: int


class MovieWatchedList(BaseModel):
    id_filmweb: str
    movies: list[MovieWatched]
    without_discord: Optional[bool] = False


@app.post("/user/watched/film/add_many")
async def add_many_movies(movies_in: MovieWatchedList):
    watched_manager = WatchedManager()

    for movie in movies_in.movies:
        result = watched_manager.add_watched_movie(
            movies_in.id_filmweb,
            movie.movie_id,
            movie.rate,
            movie.comment,
            movie.favorite,
            movie.unix_timestamp,
            movies_in.without_discord,
        )


class SeriesWatched(BaseModel):
    id_watched: Optional[int] = None
    id_filmweb: str
    series_id: int
    rate: int
    comment: Optional[str] = None
    favorite: bool = False
    unix_timestamp: int


class SeriesWatchedList(BaseModel):
    id_filmweb: str
    series: list[SeriesWatched]
    without_discord: Optional[bool] = False


@app.post("/user/watched/series/add_many")
async def add_many_series(series_in: SeriesWatchedList):
    watched_manager = WatchedManager()

    for series in series_in.series:
        result = watched_manager.add_watched_series(
            series_in.id_filmweb,
            series.series_id,
            series.rate,
            series.comment,
            series.favorite,
            series.unix_timestamp,
            series_in.without_discord,
        )


@app.post("/user/create")
async def create_user(user_in: UserIn):
    user_manager = UserManager()
    result = user_manager.create_user(user_in.id_filmweb, user_in.id_discord)
    if result is True:
        return {"message": "OK"}

    if result == "User does not exist on filmweb":
        raise HTTPException(status_code=404, detail=result)

    if result == "User already exists":
        raise HTTPException(status_code=409, detail=result)

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


@app.get("/user/watched/film/get")
async def get_movie(id_filmweb: str, movie_id: int):
    watched_manager = WatchedManager()
    result = watched_manager.get_watched_movie_with_rates(id_filmweb, movie_id)
    if result is None:
        raise HTTPException(status_code=500, detail="No movies found")
    else:
        return result


@app.get("/user/discord/destinations/get")
async def get_user_destinations(id_discord: int):
    discord_manager = DiscordManager()
    result = discord_manager.get_user_notification_destinations_by_id(id_discord)
    if result is None:
        raise HTTPException(status_code=500, detail="No destinations found")
    else:
        return result

##################################################
# SERIES 
##################################################
    
class SeriesUpdateIn(BaseModel):
    id: int
    title: str
    year: int
    other_year: Optional[int]
    poster_uri: str
    community_rate: float

@app.post("/series/update")
async def update_series(series_update_in: SeriesUpdateIn):
    series_manager = SeriesManager()

    result = series_manager.add_series_to_db(
        SeriesManagerSeries(
            id=series_update_in.id,
            title=series_update_in.title,
            year=series_update_in.year,
            other_year=series_update_in.other_year,
            poster_uri=series_update_in.poster_uri,
            community_rate=series_update_in.community_rate,
        )
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
        MovieManagerMovie(
            id=movie_update_in.id,
            title=movie_update_in.title,
            year=movie_update_in.year,
            poster_uri=movie_update_in.poster_uri,
            community_rate=movie_update_in.community_rate,
        )
    )

    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


# @app.get("/movie/get

##################################################
# TASKS
##################################################


class PostGetTasks(BaseModel):
    status: str
    types: list[str]


@app.post("/tasks/get")
async def post_get_tasks(post_get_tasks: PostGetTasks):
    # if post_get_tasks.types is not None:
    #     types = ujson.dumps(types)

    tasks_manager = TasksManager()
    result = tasks_manager.get_and_update_tasks(
        post_get_tasks.types, post_get_tasks.status
    )
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


@app.get("/task/scrap/all/users")
async def scrap_all_users():
    tasks_manager = TasksManager()
    result = tasks_manager.add_scrap_users_task()
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/task/scrap/all/movies")
async def scrap_all_movies():
    tasks_manager = TasksManager()
    result = tasks_manager.add_scrap_movies_task()
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)
    
@app.get("/task/scrap/all/series")
async def scrap_all_series():
    tasks_manager = TasksManager()
    result = tasks_manager.add_scrap_series_task()
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)

@app.get("/tasks/scrap/all/series")
async def scrap_all_series():
    tasks_manager = TasksManager()
    result = tasks_manager.add_scrap_series_task()
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)

@app.get("/tasks/update/stuck")
async def update_stuck_tasks():
    tasks_manager = TasksManager()
    result = tasks_manager.update_stuck_tasks()
    if result is True:
        return {"message": "OK"}
    else:
        raise HTTPException(status_code=500, detail=result)


@app.get("/tasks/delete/old")
async def delete_old_tasks():
    tasks_manager = TasksManager()
    result = tasks_manager.delete_old_tasks()
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
    result = discord_manager.add_user_to_guild(guild_in.id_discord, guild_in.id_guild)
    if result is True:
        return {"message": "OK"}

    if result == "User not found in database":
        raise HTTPException(status_code=404, detail=result)

    if result == "Server not configured":
        raise HTTPException(status_code=405, detail=result)

    if result is False:
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
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
