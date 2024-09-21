import datetime
import logging

import ujson

from filman_server.database.schemas import FilmWebUserWatchedMovieCreate

from .utils import (
    DiscordNotifications,
    FilmWeb,
    Task,
    Tasks,
    TaskStatus,
    TaskTypes,
    Updaters,
)


class Scraper:
    def __init__(self, headers=None, endpoint_url=None):
        self.headers = headers
        self.endpoint_url = endpoint_url
        self.fetch = Updaters(headers, endpoint_url).fetch

    def scrap(self, task: Task):
        logging.info(f"Scraping user watched movies for user: {task.task_job}")

        tasks = Tasks(self.headers, self.endpoint_url)

        last_100_watched = f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/film"
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

            if last_100_watched_data is None:
                logging.error(f"Error fetching last 100 watched for {task.task_job}")
                return "Private profile or no movies watched"

        except Exception as e:
            logging.error(f"Error fetching last 100 watched movies from filmweb: {e}")
            return "Error fetching last 100 watched movies from filmweb"

        first_time_scrap = True if user_already_watched_ids == [] else False
        user_already_watched_ids = set(user_already_watched_ids or [])

        new_movies_watched = [movie for movie in last_100_watched_data if movie[0] not in user_already_watched_ids]
        new_movies_watched_parsed = []

        logging.debug(f"Found {len(new_movies_watched)} new movies watched")

        for movie in new_movies_watched:
            try:
                logging.debug(f"Fetching user movie rate for movie from filmweb: {movie[0]}")
                movie_rate_data = self.fetch(f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/film/{movie[0]}")

                if movie_rate_data is None:
                    logging.error(f"Error fetching movie rate for movie: {movie[0]}")
                    continue

                movie_rate_data = ujson.loads(movie_rate_data)

                watched_movie_info = FilmWebUserWatchedMovieCreate(
                    id_media=movie[0],
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
                logging.error(f"Error updating data for {task.task_job}")
                return "Error updating data"

            logging.info(f"Data updated for {task.task_job}")
            return "Data updated"
        except Exception as e:
            logging.error(f"Error updating data: {e}")
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
                                filmweb_id=filmweb_id, media_type="movie", media_id=movie.id_media
                            )
                            is True
                        ):
                            logging.info(f"Notification sent for {filmweb_id}")
                        else:
                            logging.error(f"Error sending notification for {filmweb_id}")
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
                continue

        tasks.update_task_status(task_id, TaskStatus.COMPLETED)

        return True
