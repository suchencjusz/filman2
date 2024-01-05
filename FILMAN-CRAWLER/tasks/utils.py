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