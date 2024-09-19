from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

#
# USER
#

#
# lesson nr 1 - crud.py should not exist, queries should be in schemas.py....


class User(BaseModel):
    id: int
    discord_id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    discord_id: int

    class Config:
        orm_mode = True


class UserPreferences(BaseModel):
    id: int

    class Config:
        orm_mode = True


#
# MAPPINGS
#
class FilmWebUserMapping(BaseModel):
    id: int
    user_id: int
    filmweb_id: str

    class Config:
        orm_mode = True


class FilmWebUserMappingCreate(BaseModel):
    user_id: int
    filmweb_id: str

    class Config:
        orm_mode = True


# class UserPreferencesCreate(BaseModel):
#     discord_color: str

#     class Config:
#         orm_mode = True


#
# DISCORD
#


class DiscordGuilds(BaseModel):
    id: int
    discord_guild_id: int
    discord_channel_id: int

    class Config:
        orm_mode = True


class DiscordGuildsCreate(BaseModel):
    discord_guild_id: int
    discord_channel_id: int

    class Config:
        orm_mode = True


class DiscordDestinations(BaseModel):
    user_id: int
    discord_guild_id: int

    class Config:
        orm_mode = True


class DiscordDestinationsCreate(BaseModel):
    user_id: int
    discord_guild_id: int

    class Config:
        orm_mode = True


#
# LETTERBOXD
#


class LetterboxdUserMapping(BaseModel):
    letterboxd_id: str
    user_id: int

    class Config:
        orm_mode = True


#
# FILMWEB
#


class FilmWebUserMapping(BaseModel):
    filmweb_id: str
    user_id: int

    class Config:
        orm_mode = True


# MOVIES


class FilmWebMovie(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None

    class Config:
        orm_mode = True


class FilmWebMovieCreate(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None

    class Config:
        orm_mode = True


class FilmWebUserWatchedMovie(BaseModel):
    movie: FilmWebMovie
    filmweb_id: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmWebUserWatchedMovieCreate(BaseModel):
    id_media: int
    filmweb_id: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


# SERIES


class FilmWebSeries(BaseModel):
    id: int
    title: str
    year: int
    other_year: int
    poster_url: str
    community_rate: float
    critics_rate: float

    class Config:
        orm_mode = True


class FilmWebSeriesCreate(BaseModel):
    id: int
    title: str | None
    year: int | None
    other_year: int | None
    poster_url: str | None
    community_rate: float | None
    critics_rate: float | None

    class Config:
        orm_mode = True


class FilmWebUserWatchedSeries(BaseModel):
    series: FilmWebSeries
    filmweb_id: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmwebUserWatchedSeries(BaseModel):
    series: FilmWebSeries
    filmweb_id: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmwebUserWatchedSeriesCreate(BaseModel):
    id_media: int
    filmweb_id: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


#
# TASKS
#


class TaskTypes(str, Enum):
    SCRAP_FILMWEB_USER = "scrap_filmweb_user"
    SCRAP_FILMWEB_MOVIE = "scrap_filmweb_movie"
    SCRAP_FILMWEB_SERIES = "scrap_filmweb_series"
    SCRAP_FILMWEB_USER_WATCHED_MOVIES = "scrap_filmweb_user_watched_movies"
    SCRAP_FILMWEB_USER_WATCHED_SERIES = "scrap_filmweb_user_watched_series"
    SEND_DISCORD_NOTIFICATION = "send_discord_notification"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class Task(BaseModel):
    task_id: int
    task_status: TaskStatus
    task_type: TaskTypes
    task_job: str
    task_created: datetime
    task_started: Optional[datetime] = None
    task_finished: Optional[datetime] = None

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    task_status: TaskStatus
    task_type: TaskTypes
    task_job: str
    task_created: Optional[datetime] = None
    task_started: Optional[datetime] = None
    task_finished: Optional[datetime] = None

    class Config:
        orm_mode = True
