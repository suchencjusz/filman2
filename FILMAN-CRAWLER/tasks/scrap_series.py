import logging
import requests
import ujson


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Task:
    def __init__(
        self, id_task, status, type, job, unix_timestamp, unix_timestamp_last_update
    ):
        self.id_task = id_task
        self.status = status
        self.type = type
        self.job = job
        self.unix_timestamp = unix_timestamp
        self.unix_timestamp_last_update = unix_timestamp_last_update

    def __str__(self):
        return (
            f"{self.id_task} {self.status} {self.type} {self.job} {self.unix_timestamp}"
        )


class Scraper:
    def __init__(self, headers=None, series_id=None, endpoint_url=None):
        self.headers = headers
        self.series_id = series_id
        self.endpoint_url = endpoint_url

    def fetch(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logging.error(f"Error fetching {url}: HTTP {response.status_code}")
            return None
        return response.text

    def scrap(self, task):
        info_url = f"https://www.filmweb.pl/api/v1/title/{task.job}/info"
        rating_url = f"https://www.filmweb.pl/api/v1/film/{task.job}/rating"

        info_data = self.fetch(info_url)
        rating_data = self.fetch(rating_url)

        if info_data is None or rating_data is None:
            return False

        info_data = ujson.loads(info_data)
        rating_data = ujson.loads(rating_data)

        title = info_data.get("title", None)
        year = int(info_data.get("year", None))
        other_year = int(info_data.get("otherYear", 0))
        poster_url = info_data.get("posterPath", "https://vectorified.com/images/no-data-icon-23.png")
        community_rate = rating_data.get("rate", None)

        if title is None or year is None or poster_url is None:
            return False
        
        return self.update_data(
            self.series_id, title, year, other_year, poster_url, community_rate, task.id_task
        )


    def update_data(self, series_id, title, year, other_year, poster_url, community_rate, id_task):
        r = requests.post(
            f"{self.endpoint_url}/series/update",
            headers=self.headers,
            json={
                "id": int(series_id),
                "title": str(title),
                "year": int(year),
                "other_year": int(other_year),
                "poster_uri": str(poster_url),
                "community_rate": float(community_rate),
            },
        )

        if r.status_code != 200:
            logging.error(f"Error updating series data: HTTP {r.status_code}")
            logging.error(r.text)
            return False

        r = requests.get(
            f"{self.endpoint_url}/task/update?id_task={id_task}&status=done",
            headers=self.headers,
        )

        if r.status_code != 200:
            return False

        return True
