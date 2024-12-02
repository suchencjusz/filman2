import logging

import ujson

from .utils import FilmWeb, FilmWebSeries, Task, Tasks, TaskStatus, Updaters


class Scraper:
    def __init__(self, headers=None, series_id=None, endpoint_url=None):
        self.headers = headers
        self.series_id = series_id
        self.endpoint_url = endpoint_url
        self.fetch = Updaters(headers, endpoint_url).fetch

    def scrap(self, task: Task):
        logging.debug(f"Scraping series data for series: {task.task_job}")

        info_url = f"https://www.filmweb.pl/api/v1/title/{task.task_job}/info"
        rating_url = f"https://www.filmweb.pl/api/v1/film/{task.task_job}/rating"
        critics_url = f"https://www.filmweb.pl/api/v1/film/{task.task_job}/critics/rating"  # here?

        info_data = self.fetch(info_url)
        rating_data = self.fetch(rating_url)
        critics_data = self.fetch(critics_url)

        logging.debug(f"Fetched info data: {info_data}")
        logging.debug(f"Fetched rating data: {rating_data}")
        logging.debug(f"Fetched critics data: {critics_data}")

        if info_data is None or rating_data is None:
            return False

        try:
            info_data = ujson.loads(info_data)
            rating_data = ujson.loads(rating_data) if rating_data else None
            critics_data = ujson.loads(critics_data) if critics_data else None

            logging.debug(f"Info data : {info_data}")
            logging.debug(f"Rating data : {rating_data}")
            logging.debug(f"Critics data : {critics_data}")
        except Exception as e:
            logging.error(f"Error parsing series data (info, rating, critics): {e}")

        title = info_data.get("title", None)
        year = info_data.get("year", None)
        other_year = info_data.get("otherYear", None)
        poster_url = info_data.get("posterPath", "https://vectorified.com/images/no-data-icon-23.png")
        community_rate = rating_data.get("rate", None) if rating_data else None
        critics_rate = critics_data.get("rate", None) if critics_data else None

        logging.debug(f"Data for series: {title} ({year}) - {poster_url} - {community_rate} - {critics_rate}")

        if title is None or year is None or poster_url is None:
            logging.error(f"Error fetching series data for series (title/year/poster_url): {task.task_job}")
            logging.debug(f"Title: {title}, Year: {year}, Poster URL: {poster_url}")
            return False

        logging.debug(f"Updating series data for series: {task.task_job}")

        update = self.update_data(
            series_id=task.task_job,
            title=title,
            year=year,
            other_year=other_year,
            poster_url=poster_url,
            community_rate=community_rate,
            critics_rate=critics_rate,
            task_id=task.task_id,
        )

        if update:
            logging.info(f"Updated series {title} ({year})")
        else:
            logging.error(f"Error updating series {title} ({year})")

        logging.debug(f"Scraping series data for series: {task.task_job} finished")

        return update

    def update_data(
        self,
        series_id: int,
        title: str,
        year: int,
        other_year: int,
        poster_url: str,
        community_rate: float,
        critics_rate: float,
        task_id: int,
    ):
        try:
            logging.debug(f"Updating series data for series: {series_id}")

            filmweb = FilmWeb(self.headers, self.endpoint_url)
            filmweb.update_series(
                FilmWebSeries(
                    id=series_id,
                    title=title,
                    year=year,
                    other_year=other_year,
                    poster_url=poster_url,
                    community_rate=community_rate,
                    critics_rate=critics_rate,
                )
            )
            logging.debug(f"Series data updated for series: {series_id} updated")

            tasks = Tasks(self.headers, self.endpoint_url)
            tasks.update_task_status(task_id, TaskStatus.COMPLETED)
            logging.debug(f"Task status updated for task: {task_id}")

            return True
        except Exception as e:
            logging.error(f"Error updating series data for series: {series_id}")
            logging.error(e)
            return False
