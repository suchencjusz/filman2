import datetime
import logging

import ujson

from filman_server.database.schemas import FilmWebUserWatchedMovieCreate

from .utils import (
    FilmWeb,
    FilmWebMovie,
    Task,
    Tasks,
    TaskStatus,
    TaskTypes,
    Updaters,
)

# TODO make it more robust and add
# https://www.filmweb.pl/api/v1/film/628/critics/rating


class Scraper:
    def __init__(self, headers=None, movie_id=None, endpoint_url=None):
        self.headers = headers
        self.movie_id = movie_id
        self.endpoint_url = endpoint_url
        self.fetch = Updaters(headers, endpoint_url).fetch

    def scrap(self, task: Task):
        info_url = f"https://www.filmweb.pl/api/v1/title/{task.task_job}/info"
        rating_url = f"https://www.filmweb.pl/api/v1/film/{task.task_job}/rating"
        crictics_url = f"https://www.filmweb.pl/api/v1/film/{task.task_job}/critics/rating"

        info_data = self.fetch(info_url)
        rating_data = self.fetch(rating_url)
        crictics_data = self.fetch(crictics_url)

        crictics_rate = None

        if info_data is not None and rating_data is not None:
            info_data = ujson.loads(info_data)
            rating_data = ujson.loads(rating_data)
        else:
            return False

        if crictics_data is not None:
            crictics_data = ujson.loads(crictics_data)
        else:
            crictics_rate = None

        # TODO critics_rate typo fix

        title = info_data.get("title", None)
        year = int(info_data.get("year", None))
        poster_url = info_data.get("posterPath", "https://vectorified.com/images/no-data-icon-23.png")
        community_rate = rating_data.get("rate", None)
        critics_rate = critics_rate.get("rate", None)

        if title is None or year is None or poster_url is None:
            return False

        update = self.update_data(
            self.movie_id,
            title,
            year,
            poster_url,
            community_rate,
            critics_rate,
            task.task_id,
        )

        if update is True:
            logging.info(f"Updated movie {title} ({year})")

        return update

    def update_data(self, movie_id, title, year, poster_url, community_rate, critics_rate, task_id):
        try:
            filmweb = FilmWeb(self.headers, self.endpoint_url)
            filmweb.update_movie(
                FilmWebMovie(
                    id=movie_id,
                    title=title,
                    year=year,
                    poster_url=poster_url,
                    community_rate=community_rate,
                    critics_rate=critics_rate,
                )
            )

            tasks = Tasks(self.headers, self.endpoint_url)
            tasks.update_task_status(task_id, TaskStatus.COMPLETED)

        except Exception as e:
            logging.error(f"Error updating movie data: {e}")
            return False

        return True
