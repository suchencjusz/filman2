import datetime
import logging
from urllib.parse import quote

import requests

from filman_server.database.schemas import (
    FilmWebMovie,
    FilmWebSeries,
    FilmWebUserWatchedMovieCreate,
    FilmWebUserWatchedSeriesCreate,
    Task,
    TaskStatus,
    TaskTypes,
)

DEFAULT_TIMEOUT = (5, 15)
SERVER_HEADERS = {"Accept": "application/json"}


class Updaters:
    def __init__(self, headers, endpoint_url, session: requests.Session | None = None):
        self.headers = headers
        self.endpoint_url = endpoint_url.rstrip("/") if endpoint_url else endpoint_url
        self.session = session

    def _request(self, method: str, url: str, timeout=DEFAULT_TIMEOUT, **kwargs) -> requests.Response | None:
        is_server_url = bool(self.endpoint_url and url.startswith(self.endpoint_url))
        if "headers" not in kwargs:
            kwargs["headers"] = SERVER_HEADERS if is_server_url else self.headers

        http = self.session or requests
        try:
            return http.request(method.upper(), url, timeout=timeout, **kwargs)
        except requests.RequestException as e:
            logging.error(f"Request error ({method.upper()} {url}): {e}")
            return None

    def fetch(self, url, method="GET", **kwargs) -> str | None:
        """
        Fetch data from a URL using the specified HTTP method.

        :param url: The URL to fetch data from.
        :param method: The HTTP method to use ('GET', 'POST', 'DELETE', 'PUT').
        :param kwargs: Additional arguments to pass to the requests method.
        :return: The response text or None if an error occurred.
        """
        method = method.upper()
        if method not in {"GET", "POST", "DELETE", "PUT"}:
            logging.error(f"Unsupported HTTP method: {method}")
            return None

        response = self._request(method, url, **kwargs)
        if response is None:
            return None

        if response.status_code != 200:
            logging.error(f"Error fetching {url}: HTTP {response.status_code}")
            return None

        return response.text

    def _call_server(self, method: str, path: str, error_context: str, **kwargs) -> bool:
        response = self._request(method, f"{self.endpoint_url}{path}", **kwargs)
        if response is None:
            logging.error(f"{error_context}: request failed")
            return False

        if response.status_code != 200:
            logging.error(f"{error_context}: HTTP {response.status_code} - {response.text}")
            return False

        return True


class Tasks(Updaters):
    def update_task_status(self, task_id: int, task_status: TaskStatus) -> bool:
        return self._call_server(
            "GET",
            f"/tasks/update/status/{task_id}/{task_status.value}",
            "Error updating task status",
        )

    def create_task(self, task: Task) -> bool:
        return self._call_server(
            "POST",
            "/tasks/create",
            "Error creating task",
            json={
                "task_id": task.task_id,
                "task_status": task.task_status.value,
                "task_type": task.task_type.value,
                "task_job": task.task_job,
                "task_created": task.task_created.isoformat(),
            },
        )


class DiscordNotifications(Updaters):
    def send_notification(self, filmweb_id: str, media_type: str, media_id: int) -> bool:
        tasks = Tasks(self.headers, self.endpoint_url, session=self.session)
        created = tasks.create_task(
            Task(
                task_id=0,
                task_status=TaskStatus.QUEUED,
                task_type=TaskTypes.SEND_DISCORD_NOTIFICATION,
                task_job=f"{filmweb_id},{media_type},{media_id}",
                task_created=datetime.datetime.now(),
            )
        )

        if not created:
            logging.error("Error creating task: SEND_DISCORD_NOTIFICATION")
            return False

        return True


class FilmWeb(Updaters):
    def update_series(self, series: FilmWebSeries) -> bool:
        return self._call_server(
            "POST",
            "/filmweb/series/update",
            "Error updating series data",
            json=series.model_dump(),
        )

    def add_watched_series(self, info: FilmWebUserWatchedSeriesCreate) -> bool:
        return self._call_server(
            "POST",
            "/filmweb/user/watched/series/add",
            "Error adding watched series",
            json={
                "id_media": int(info.id_media),
                "filmweb_id": str(info.filmweb_id),
                "date": info.date.isoformat(),
                "rate": int(info.rate),
                "comment": info.comment,
                "favorite": bool(info.favorite),
            },
        )

    def update_movie(self, movie: FilmWebMovie) -> bool:
        return self._call_server(
            "POST",
            "/filmweb/movie/update",
            "Error updating movie data",
            json=movie.model_dump(),
        )

    def add_watched_movie(self, info: FilmWebUserWatchedMovieCreate) -> bool:
        return self._call_server(
            "POST",
            "/filmweb/user/watched/movies/add",
            "Error adding watched movie",
            json={
                "id_media": int(info.id_media),
                "filmweb_id": str(info.filmweb_id),
                "date": info.date.isoformat(),
                "rate": int(info.rate),
                "comment": info.comment,
                "favorite": bool(info.favorite),
            },
        )


def fetch_filmweb_user_id(
    filmweb_id: str,
    headers: dict | None,
    session: requests.Session | None = None,
) -> int | None:
    """Resolve a Filmweb username into its numeric Filmweb user ID."""
    url = f"https://www.filmweb.pl/api/v1/users/{quote(filmweb_id)}/id"
    http = session or requests
    try:
        response = http.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        logging.error(f"Error fetching Filmweb user id for {filmweb_id}: {exc}")
        return None

    if response.status_code != 200:
        logging.error(f"Filmweb user id lookup failed for {filmweb_id}: HTTP {response.status_code}")
        return None

    try:
        user_id = response.json().get("userId")
        return int(user_id) if user_id is not None else None
    except Exception as exc:
        logging.error(f"Error parsing Filmweb user id response for {filmweb_id}: {exc}")
        return None


def extract_vote_media_ids(votes: list) -> list[int]:
    """Extract numeric media IDs from Filmweb votes API items."""
    media_ids: list[int] = []
    for vote in votes:
        if isinstance(vote, dict) and "id" in vote:
            vote_id = vote.get("id")
            media_id = vote_id.get("id") if isinstance(vote_id, dict) else vote_id
        elif isinstance(vote, (list, tuple)) and len(vote) > 0:
            media_id = vote[0]
        else:
            media_id = None

        if media_id is not None:
            media_ids.append(media_id)
    return media_ids
