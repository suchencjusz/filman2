from pydantic import BaseModel
from datetime import datetime

#
# USER
#


class User(BaseModel):
    id: int
    filmweb_id: str
    discord_id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    filmweb_id: str
    discord_id: int

    class Config:
        orm_mode = True


class UserPreferences(BaseModel):
    id: int
    discord_color: str

    class Config:
        orm_mode = True


class UserPreferencesCreate(BaseModel):
    discord_color: str

    class Config:
        orm_mode = True


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
# FILMWEB
#


class FilmWebMovie(BaseModel):
    id: int
    title: str
    year: int
    poster_url: str
    community_rate: float

    class Config:
        orm_mode = True


class FilmWebMovieCreate(BaseModel):
    id: int
    title: str | None
    year: int | None
    poster_url: str | None
    community_rate: float | None

    class Config:
        orm_mode = True


class FilmWebUserWatchedMovie(BaseModel):
    movie: FilmWebMovie
    id_filmweb: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmWebUserWatchedMovieCreate(BaseModel):
    id_media: int
    id_filmweb: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmwebUserWatchedSeries(BaseModel):
    series: FilmWebMovie
    id_filmweb: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True


class FilmwebUserWatchedSeriesCreate(BaseModel):
    id_media: int
    id_filmweb: str

    date: datetime
    rate: int | None
    comment: str | None
    favorite: bool

    class Config:
        orm_mode = True

#
# TASKS
#

class Task(BaseModel):
    task_id: int
    task_status: str
    task_type: str
    task_job: str
    task_created: datetime
    task_started: datetime | None
    task_finished: datetime | None