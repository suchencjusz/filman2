from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

#
# USER
#

#
# lesson nr 1 - crud.py should not exist, queries should be in schemas.py....


class User(BaseModel):
    id: int
    discord_id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    discord_id: int
    model_config = ConfigDict(from_attributes=True)


class UserPreferences(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


#
# MAPPINGS
#
class FilmWebUserMapping(BaseModel):
    id: int
    user_id: int
    filmweb_id: str
    model_config = ConfigDict(from_attributes=True)


class FilmWebUserMappingCreate(BaseModel):
    user_id: int
    filmweb_id: str
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


class DiscordGuildsCreate(BaseModel):
    discord_guild_id: int
    discord_channel_id: int
    model_config = ConfigDict(from_attributes=True)


class DiscordDestinations(BaseModel):
    user_id: int
    discord_guild_id: int
    model_config = ConfigDict(from_attributes=True)


class DiscordDestinationsCreate(BaseModel):
    user_id: int
    discord_guild_id: int
    model_config = ConfigDict(from_attributes=True)


#
# LETTERBOXD
#


class LetterboxdUserMapping(BaseModel):
    letterboxd_id: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)


# MOVIES


class FilmWebMovie(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None
    model_config = ConfigDict(from_attributes=True)


class FilmWebMovieCreate(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None
    model_config = ConfigDict(from_attributes=True)


class FilmWebUserWatchedMovie(BaseModel):
    movie: FilmWebMovie
    filmweb_id: str

    date: datetime
    rate: int | None = None
    comment: str | None = None
    favorite: bool
    model_config = ConfigDict(from_attributes=True)


class FilmWebUserWatchedMovieCreate(BaseModel):
    id_media: int
    filmweb_id: str

    date: datetime
    rate: int | None = None
    comment: str | None = None
    favorite: bool
    model_config = ConfigDict(from_attributes=True)


# SERIES


class FilmWebSeries(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    other_year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None
    model_config = ConfigDict(from_attributes=True)


class FilmWebSeriesCreate(BaseModel):
    id: int
    title: str | None = None
    year: int | None = None
    other_year: int | None = None
    poster_url: str | None = None
    community_rate: float | None = None
    critics_rate: float | None = None
    model_config = ConfigDict(from_attributes=True)


class FilmWebUserWatchedSeries(BaseModel):
    series: FilmWebSeries
    filmweb_id: str

    date: datetime
    rate: int | None = None
    comment: str | None = None
    favorite: bool
    model_config = ConfigDict(from_attributes=True)


class FilmwebUserWatchedSeriesCreate(BaseModel):
    id_media: int
    filmweb_id: str

    date: datetime
    rate: int | None = None
    comment: str | None = None
    favorite: bool
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    task_status: TaskStatus
    task_type: TaskTypes
    task_job: str
    task_created: Optional[datetime] = None
    task_started: Optional[datetime] = None
    task_finished: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
