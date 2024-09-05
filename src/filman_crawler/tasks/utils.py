import logging
import requests
import ujson

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class TaskTypes(str, Enum):
    SCRAP_USER = "scrap_user"
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


class Updaters:
    def __init__(self, headers, endpoint_url):
        self.headers = headers
        self.endpoint_url = endpoint_url


class Tasks(Updaters):
    def update_task_status(self, task_id: int, task_status: TaskStatus):
        r = requests.get(
            f"{self.endpoint_url}/tasks/update/task/status/{task_id}/{task_status.value}",
            headers=self.headers,
        )

        if r.status_code != 200:
            logging.error(f"Error updating task status: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True


class DiscordNotifications(Updaters):
    def send_notification(self, filmweb_id: str):
        r = requests.post(
            f"{self.endpoint_url}/tasks/create",
            headers=self.headers,
            json=Task(
                task_id=0,
                task_status=TaskStatus.QUEUED,
                task_type=TaskTypes.SEND_DISCORD_NOTIFICATION,
                task_job=filmweb_id,
                task_created=datetime.now(),
            ),
        )

        if r.status_code != 200:
            logging.error(f"Error sending discord notification: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True


class FilmWeb(Updaters):
    class FilmWebMovie(BaseModel):
        id: int
        title: str
        year: int
        poster_url: str
        community_rate: float

    class FilmWebSeries(BaseModel):
        id: int
        title: str
        year: int
        other_year: int
        poster_url: str
        community_rate: float

    class FilmWebUserWatchedMovie(BaseModel):
        id_media: int
        id_filmweb: str
        date: datetime
        rate: int
        comment: Optional[str]
        favorite: bool

    def update_movie(self, movie: FilmWebMovie):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/update/movie",
            headers=self.headers,
            json={
                "id": int(movie.id),
                "title": str(movie.title),
                "year": int(movie.year),
                "poster_url": str(movie.poster_url),
                "community_rate": float(movie.community_rate),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error updating movie data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def update_series(self, series: FilmWebSeries):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/update/series",
            headers=self.headers,
            json={
                "id": int(series.id),
                "title": str(series.title),
                "year": int(series.year),
                "other_year": int(series.other_year),
                "poster_url": str(series.poster_url),
                "community_rate": float(series.community_rate),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error updating series data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def add_watched_movie(self, info: FilmWebUserWatchedMovie):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/watched/movies/add",
            headers=self.headers,
            json={
                "id_media": int(info.id_media),
                "id_filmweb": str(info.id_filmweb),
                "date": info.date.isoformat(),
                "rate": int(info.rate),
                "comment": info.comment,
                "favorite": bool(info.favorite),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error adding watched movie: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True
