import logging
import requests
import ujson

from .utils import Task, TaskTypes, TaskStatus
from .utils import Tasks, FilmWeb

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Scraper:
    def __init__(self, headers=None, movie_id=None, endpoint_url=None):
        self.headers = headers
        self.movie_id = movie_id
        self.endpoint_url = endpoint_url

    def fetch(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logging.error(f"Error fetching {url}: HTTP {response.status_code}")
            return None
        return response.text

    def scrap(self, task: Task):
        info_url = f"https://www.filmweb.pl/api/v1/title/{task.task_job}/info"
        rating_url = f"https://www.filmweb.pl/api/v1/film/{task.task_job}/rating"

        info_data = self.fetch(info_url)
        rating_data = self.fetch(rating_url)

        if info_data is None or rating_data is None:
            return False

        info_data = ujson.loads(info_data)
        rating_data = ujson.loads(rating_data)

        title = info_data.get("title", None)
        year = int(info_data.get("year", None))
        poster_url = info_data.get("posterPath", "https://vectorified.com/images/no-data-icon-23.png")
        community_rate = rating_data.get("rate", None)

        if title is None or year is None or poster_url is None:
            return False

        update = self.update_data(self.movie_id, title, year, poster_url, community_rate, task.task_id)

        if update is True:
            logging.info(f"Updated movie {title} ({year})")

        return update

    def update_data(self, movie_id, title, year, poster_url, community_rate, task_id):
        try:
            filmweb = FilmWeb(self.headers, self.endpoint_url)
            filmweb.update_movie(
                FilmWeb.FilmWebMovie(
                    id=movie_id,
                    title=title,
                    year=year,
                    poster_url=poster_url,
                    community_rate=community_rate,
                )
            )

            tasks = Tasks(self.headers, self.endpoint_url)
            tasks.update_task_status(task_id, TaskStatus.COMPLETED)

        except Exception as e:
            logging.error(f"Error updating movie data: {e}")
            return False

        return True
