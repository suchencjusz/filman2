import datetime
import logging

import requests
import ujson

from filman_server.database.schemas import (
    FilmWebMovie,
    FilmWebSeries,
    FilmWebUserWatchedMovieCreate,
    FilmWebUserWatchedSeriesCreate,
    Task,
    TaskStatus,
    TaskTypes,
)


class Updaters:
    def __init__(self, headers, endpoint_url):
        self.headers = headers
        self.endpoint_url = endpoint_url

    def fetch(self, url, method="GET", **kwargs) -> str | None:
        """
        Fetch data from a URL using the specified HTTP method.

        :param url: The URL to fetch data from.
        :param method: The HTTP method to use ('GET', 'POST', 'DELETE', 'PUT').
        :param kwargs: Additional arguments to pass to the requests method.
        :return: The response text or None if an error occurred.
        """
        method = method.upper()

        kwargs["headers"] = self.headers

        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, **kwargs)
            elif method == "PUT":
                response = requests.put(url, **kwargs)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code != 200:
                logging.error(f"Error fetching {url}: HTTP {response.status_code}")
                return None

            return response.text
        except Exception as e:
            logging.error(f"Exception during fetch: {e}")
            return None


class Tasks(Updaters):
    def update_task_status(self, task_id: int, task_status: TaskStatus):
        r = requests.get(
            f"{self.endpoint_url}/tasks/update/status/{task_id}/{task_status.value}",
            headers=self.headers,
        )

        if r.status_code != 200:
            logging.error(f"Error updating task status: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def create_task(self, task: Task):
        r = requests.post(
            f"{self.endpoint_url}/tasks/create",
            headers=self.headers,
            json={
                "task_id": task.task_id,
                "task_status": task.task_status.value,
                "task_type": task.task_type.value,
                "task_job": task.task_job,
                "task_created": task.task_created.isoformat(),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error creating task: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True


class DiscordNotifications(Updaters):
    def send_notification(self, filmweb_id: str, media_type: str, media_id: int):

        task = Tasks(self.headers, self.endpoint_url)

        task = task.create_task(
            Task(
                task_id=0,
                task_status=TaskStatus.QUEUED,
                task_type=TaskTypes.SEND_DISCORD_NOTIFICATION,
                task_job=f"{filmweb_id},{media_type},{media_id}",
                task_created=datetime.datetime.now(),
            )
        )

        if not task:
            logging.error("Error creating task: SEND_DISCORD_NOTIFICATION")
            return False

        return True


class FilmWeb(Updaters):
    def update_series(self, series: FilmWebSeries):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/series/update",
            headers=self.headers,
            json=series.model_dump(),
        )

        if r.status_code != 200:
            logging.error(f"Error updating series data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def add_watched_series(self, info: FilmWebUserWatchedSeriesCreate):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/user/watched/series/add",
            headers=self.headers,
            json={
                "id_media": int(info.id_media),
                "filmweb_id": str(info.filmweb_id),
                "date": info.date.isoformat(),
                "rate": int(info.rate),
                "comment": info.comment,
                "favorite": bool(info.favorite),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error adding watched series: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def update_movie(self, movie: FilmWebMovie):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/movie/update",
            headers=self.headers,
            json=movie.model_dump(),
        )

        if r.status_code != 200:
            logging.error(f"Error updating movie data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    def add_watched_movie(self, info: FilmWebUserWatchedMovieCreate):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/user/watched/movies/add",
            headers=self.headers,
            json={
                "id_media": int(info.id_media),
                "filmweb_id": str(info.filmweb_id),
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
