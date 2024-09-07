import logging

import requests
import ujson


class Task:
    def __init__(self, id_task, status, type, job, unix_timestamp, unix_timestamp_last_update):
        self.id_task = id_task
        self.status = status
        self.type = type
        self.job = job
        self.unix_timestamp = unix_timestamp
        self.unix_timestamp_last_update = unix_timestamp_last_update

    def __str__(self):
        return f"{self.id_task} {self.status} {self.type} {self.job} {self.unix_timestamp}"


class Watched:
    def __init__(self, id_watched, id_filmweb, series_id, rate, comment, favorite, unix_timestamp):
        self.id_watched = id_watched
        self.id_filmweb = id_filmweb
        self.series_id = series_id
        self.rate = rate
        self.comment = comment
        self.favorite = favorite
        self.unix_timestamp = unix_timestamp

    def __str__(self):
        return f"{self.id_watched} {self.id_filmweb} {self.series_id} {self.rate} {self.comment} {self.favorite} {self.unix_timestamp}"

    def to_dict(self):
        return {
            "id_watched": self.id_watched,
            "id_filmweb": self.id_filmweb,
            "series_id": self.series_id,
            "rate": self.rate,
            "comment": self.comment,
            "favorite": self.favorite,
            "unix_timestamp": self.unix_timestamp,
        }


# https://www.filmweb.pl/api/v1/user/tirstus/vote/film

# https://www.filmweb.pl/api/v1/user/tirstus/vote/film/783759

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
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
        last_100_watched = f"https://www.filmweb.pl/api/v1/user/{task.job}/vote/serial"
        user_already_watched = f"{self.endpoint_url}/user/watched/series/all?id_filmweb={task.job}"

        last_100_watched_data = self.fetch(last_100_watched)
        user_already_watched_data = self.fetch(user_already_watched)

        first_time_scrap = user_already_watched_data is None

        if last_100_watched_data is None:
            self.update_task_status_done(task.id_task)
            return "Private profile"

        last_100_watched_data = ujson.loads(last_100_watched_data)

        if user_already_watched_data is None:
            user_already_watched_data = []
        else:
            user_already_watched_data = ujson.loads(user_already_watched_data)

            user_already_watched_data = list(map(lambda x: x["series_id"], user_already_watched_data))

        new_series_id = []

        for filmweb_watched in last_100_watched_data:
            if filmweb_watched[0] not in user_already_watched_data:
                new_series_id.append(filmweb_watched[0])

        if len(new_series_id) == 0:
            self.update_task_status_done(task.id_task)
            return "No new series"

        new_series_watched = []

        for series_id in new_series_id:
            series_rate_data = self.fetch(f"https://www.filmweb.pl/api/v1/user/{task.job}/vote/serial/{series_id}")

            if series_rate_data is None:
                continue

            series_rate_data = ujson.loads(series_rate_data)

            series_watched = Watched(
                None,
                task.job,
                series_id=series_id,
                rate=series_rate_data["rate"],
                comment=series_rate_data.get("comment", None),
                favorite=bool(series_rate_data.get("favorite", False)),
                unix_timestamp=series_rate_data["timestamp"],
            )

            new_series_watched.append(series_watched)

        return self.update_data(
            task.job,
            new_series_watched,
            task.id_task,
            first_time_scrap,
        )

    def update_data(
        self,
        filmweb_id: str,
        series_watched: list,
        id_task: int,
        without_discord: bool,
    ):
        if len(filmweb_id) == 0:
            return "No new series"

        r = requests.post(
            f"{self.endpoint_url}/user/watched/series/add_many",
            json={
                "id_filmweb": filmweb_id,
                "series": [series.to_dict() for series in series_watched],
                "without_discord": without_discord,
            },
        )

        if r.status_code != 200:
            logging.error(f"Error adding series: HTTP {r.status_code}")
            logging.error(r.text)
            return "Error adding series"

        self.update_task_status_done(id_task)

        if r.status_code != 200:
            return "Error updating task"

        return True

    def update_task_status_done(self, id_task: int):
        r = requests.get(f"{self.endpoint_url}/task/update?id_task={id_task}&status=done")

        if r.status_code != 200:
            return False

        return True
