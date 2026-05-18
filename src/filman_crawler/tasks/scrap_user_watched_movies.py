import datetime
import logging

from urllib.parse import quote

import requests
import ujson

from filman_server.database.schemas import FilmWebUserWatchedMovieCreate

from .utils import DiscordNotifications, FilmWeb, Task, Tasks, TaskStatus, TaskTypes, Updaters


class Scraper:
    def __init__(self, headers=None, endpoint_url=None):
        self.headers = headers
        self.endpoint_url = endpoint_url
        self.fetch = Updaters(headers, endpoint_url).fetch
        self._filmweb_user_id_cache: dict[str, int] = {}

    def _fetch_filmweb_user_id(self, filmweb_id: str) -> int | None:
        url = f"https://www.filmweb.pl/api/v1/users/{quote(filmweb_id)}/id"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
        except Exception as exc:
            logging.error(f"Error fetching Filmweb user id for {filmweb_id}: {exc}")
            return None

        if response.status_code != 200:
            logging.error(
                f"Filmweb user id lookup failed for {filmweb_id}: HTTP {response.status_code}"
            )
            return None

        try:
            user_id = response.json().get("userId")
            return int(user_id) if user_id is not None else None
        except Exception as exc:
            logging.error(f"Error parsing Filmweb user id response for {filmweb_id}: {exc}")
            return None

    def _resolve_filmweb_user_id(self, filmweb_id: str) -> int | None:
        if filmweb_id in self._filmweb_user_id_cache:
            return self._filmweb_user_id_cache[filmweb_id]

        filmweb_user_id = self._fetch_filmweb_user_id(filmweb_id)
        if filmweb_user_id is None:
            return None

        self._filmweb_user_id_cache[filmweb_id] = filmweb_user_id
        return filmweb_user_id

    def scrap(self, task: Task):
        logging.info(f"Scraping user watched movies for user: {task.task_job}")

        tasks = Tasks(self.headers, self.endpoint_url)

        filmweb_user_id = self._resolve_filmweb_user_id(task.task_job)
        if filmweb_user_id is None:
            logging.error(f"Error resolving Filmweb user id for {task.task_job}")
            return "Error resolving Filmweb user id"

        last_100_watched = f"https://www.filmweb.pl/api/v1/users/{filmweb_user_id}/votes/film"
        user_already_watched = f"{self.endpoint_url}/filmweb/user/watched/movies/get_all?filmweb_id={task.task_job}"

        try:
            logging.debug(f"Fetching user already watched movies from: {user_already_watched}")
            user_already_watched_data = self.fetch(user_already_watched, params={"filmweb_id": task.task_job})
            user_already_watched_data = ujson.loads(user_already_watched_data)

            if user_already_watched is not None or user_already_watched_data != []:
                user_already_watched_ids = [movie["movie"]["id"] for movie in user_already_watched_data]
            else:
                user_already_watched_ids = []

        except Exception as e:
            logging.error(f"Error fetching user already watched movies: {e}")
            return "Error fetching user already watched movies"

        try:
            logging.debug(f"Fetching last 100 watched movies from (filmweb): {last_100_watched}")
            last_100_watched_data = self.fetch(last_100_watched)
            last_100_watched_data = ujson.loads(last_100_watched_data)

            votes = []
            if isinstance(last_100_watched_data, dict):
                votes = last_100_watched_data.get("votes", [])
            elif isinstance(last_100_watched_data, list):
                votes = last_100_watched_data
            else:
                votes = []

            if last_100_watched_data is None:
                logging.error(f"Error fetching last 100 watched for {task.task_job}")
                return "Private profile or no movies watched"

        except Exception as e:
            logging.error(f"Error fetching last 100 watched movies from filmweb: {e}")
            return "Error fetching last 100 watched movies from filmweb"

        first_time_scrap = True if user_already_watched_ids == [] else False

        user_already_watched_ids = set(user_already_watched_ids or [])

        movie_ids = []
        for vote in votes:
            if isinstance(vote, dict) and "id" in vote:
                vote_id = vote.get("id")
                if isinstance(vote_id, dict):
                    movie_id = vote_id.get("id")
                else:
                    movie_id = vote_id
            elif isinstance(vote, (list, tuple)) and len(vote) > 0:
                movie_id = vote[0]
            else:
                movie_id = None

            if movie_id is not None:
                movie_ids.append(movie_id)

        new_movies_watched = [movie_id for movie_id in movie_ids if movie_id not in user_already_watched_ids]
        new_movies_watched_parsed = []

        logging.debug(f"Found {len(new_movies_watched)} new movies watched")

        for movie_id in new_movies_watched:
            try:
                logging.debug(f"Fetching user movie rate for movie from filmweb: {movie_id}")
                movie_rate_data = self.fetch(
                    f"https://www.filmweb.pl/api/v1/users/{filmweb_user_id}/votes/film/{movie_id}"
                )

                if movie_rate_data is None:
                    logging.error(f"Error fetching movie rate for movie: {movie_id}")
                    continue

                movie_rate_data = ujson.loads(movie_rate_data)

                watched_movie_info = FilmWebUserWatchedMovieCreate(
                    id_media=movie_id,
                    filmweb_id=task.task_job,
                    date=datetime.datetime.fromtimestamp(movie_rate_data["timestamp"] / 1000),
                    rate=movie_rate_data.get("rate", 0),
                    comment=movie_rate_data.get("comment", None),
                    favorite=bool(movie_rate_data.get("favorite", False)),
                )

                new_movies_watched_parsed.append(watched_movie_info)
            except Exception as e:
                logging.error(f"Error parsing movie data: {e}")
                continue

        logging.info(f"Found {len(new_movies_watched_parsed)} new movies watched")

        if len(new_movies_watched_parsed) == 0:
            tasks.update_task_status(task.task_id, TaskStatus.COMPLETED)
            return "No new movies watched"

        logging.debug("Preparing to update data")

        try:
            update = self.update_data(
                filmweb_id=task.task_job,
                movies_watched=new_movies_watched_parsed,
                first_time_scrap=first_time_scrap,
                task_id=task.task_id,
            )

            if update is False:
                logging.error(f"Error updating movies data for {task.task_job}")
                return "Error updating movies data"

            logging.info(f"Data movies updated for {task.task_job}")
            return "Data updated"
        except Exception as e:
            logging.error(f"Error updating movies data: {e}")
            return "Error updating data"

    def update_data(
        self,
        filmweb_id: str,
        movies_watched: list[FilmWebUserWatchedMovieCreate],
        first_time_scrap: bool,
        task_id: int,
    ):
        logging.info(f"Updating data for {filmweb_id} with {len(movies_watched)} movies")

        filmweb = FilmWeb(self.headers, self.endpoint_url)
        tasks = Tasks(self.headers, self.endpoint_url)
        dc_notifications = DiscordNotifications(self.headers, self.endpoint_url)

        for movie in movies_watched:

            try:
                if filmweb.add_watched_movie(movie):
                    if first_time_scrap is False:
                        if (
                            dc_notifications.send_notification(
                                filmweb_id=filmweb_id,
                                media_type="movie",
                                media_id=movie.id_media,
                            )
                            is True
                        ):
                            logging.info(f"Notification sent for movies: {filmweb_id}")
                        else:
                            logging.error(f"Error sending notification for movies: {filmweb_id}")
                            continue
                else:
                    logging.error(f"Error updating movie data for {filmweb_id}")
                    continue

                tasks.create_task(
                    Task(
                        task_id=0,
                        task_status=TaskStatus.QUEUED,
                        task_type=TaskTypes.SCRAP_FILMWEB_MOVIE,
                        task_job=str(movie.id_media),
                        task_created=datetime.datetime.now(),
                    )
                )

            except Exception as e:
                logging.error(f"Exception while updating movie data: {e}")
                logging.error(e)
                continue

        tasks.update_task_status(task_id, TaskStatus.COMPLETED)

        return True
