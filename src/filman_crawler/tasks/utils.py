import logging
import requests
import ujson

from datetime import datetime

from filman_server.database.schemas import (
    FilmWebMovie,
    FilmWebSeries,
    FilmWebUserWatchedMovie,
    Task,
    TaskStatus,
    TaskTypes,
)

import requests


def fetch(url, method="GET", **kwargs):
    """
    Fetch data from a URL using the specified HTTP method.

    :param url: The URL to fetch data from.
    :param method: The HTTP method to use ('GET', 'POST', 'DELETE', 'PUT').
    :param kwargs: Additional arguments to pass to the requests method.
    :return: The response text or None if an error occurred.
    """
    method = method.upper()
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

        try:
            return response.json()
        except ValueError:
            return response.text
    except Exception as e:
        logging.error(f"Exception during fetch: {e}")
        return None


class Updaters:
    def __init__(self, headers, endpoint_url):
        self.headers = headers
        self.endpoint_url = endpoint_url


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

    def update_movie(self, movie: FilmWebMovie):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/movie/update",
            headers=self.headers,
            json={
                "id": int(movie.id),
                "title": str(movie.title),
                "year": int(movie.year),
                "other_year": int(movie.other_year),
                "poster_url": str(movie.poster_url),
                "community_rate": float(movie.community_rate),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error updating movie data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        return True

    # def update_series(self, series: FilmWebSeries):
    #     r = requests.post(
    #         f"{self.endpoint_url}/filmweb/update/series", # also endpoint  to change
    #         headers=self.headers,
    #         json={
    #             "id": int(series.id),
    #             "title": str(series.title),
    #             "year": int(series.year),
    #             "other_year": int(series.other_year),
    #             "poster_url": str(series.poster_url),
    #             "community_rate": float(series.community_rate),
    #         },
    #     )

    #     if r.status_code != 200:
    #         logging.error(f"Error updating series data: HTTP {r.status_code}")
    #         logging.error(r.text)
    #         return False

    #     return True

    def add_watched_movie(self, info: FilmWebUserWatchedMovie):
        r = requests.post(
            f"{self.endpoint_url}/filmweb/user/watched/movies/add",
            headers=self.headers,
            json={
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
