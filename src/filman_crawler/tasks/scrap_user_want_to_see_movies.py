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

        want_to_see_movies = f"https://www.filmweb.pl/api/v1/user/{task.task_job}/want2see/film"

        try:
            logging.debug(f"Fetching user want to see movies from: {want_to_see_movies}")
            want_to_see_movies_data = self.fetch(want_to_see_movies)

            if want_to_see_movies_data is None:
                logging.error(f"Error fetching want to see movies for {task.task_job}")
                return "Private profile or no movies watched"

            want_to_see_movies_data = ujson.loads(want_to_see_movies_data)

        except Exception as e:
            logging.error(f"Error fetching want to see movies: {e}")
            return "Error fetching want to see movies"

        for movie in want_to_see_movies_data:
            try:
                tasks.create_task(
                    Task(
                        task_id=0,
                        task_status=TaskStatus.QUEUED,
                        task_type=TaskTypes.SCRAP_FILMWEB_MOVIE,
                        task_job=str(movie["entity"]),
                        task_created=datetime.datetime.now(),
                    )
                )
            except Exception as e:
                logging.error(f"Error creating task for movie: {e}")
                return "Error creating task for movie"
