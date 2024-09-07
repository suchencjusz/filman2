import datetime
import logging

import requests
import ujson

from .utils import DiscordNotifications, FilmWeb, Task, Tasks, TaskStatus, TaskTypes

# https://www.filmweb.pl/api/v1/user/tirstus/vote/film

# https://www.filmweb.pl/api/v1/user/tirstus/vote/film/783759

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Scraper:
    def __init__(self, headers=None, endpoint_url=None):
        self.headers = headers
        self.endpoint_url = endpoint_url

    def fetch(self, url, params=None):
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            logging.error(f"Error fetching {url}: HTTP {response.status_code}")
            return None

        # r = requests.get(
        #         f"{CORE_ENDPOINT}/tasks/get/task/to_do",
        #         params={"task_types": TASK_TYPES},
        #         headers=HEADERS,
        #     )

        return response.text

    def scrap(self, task):
        filmweb = FilmWeb(self.headers, self.endpoint_url)
        tasks = Tasks(self.headers, self.endpoint_url)

        last_100_watched = f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/film"
        user_already_watched = f"{self.endpoint_url}/filmweb/watched/movies/get/ids"

        try:
            last_100_watched_data = self.fetch(last_100_watched)
            user_already_watched_data = self.fetch(user_already_watched, params={"filmweb_id": task.task_job})
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return "Error fetching data"

        if last_100_watched_data is None:
            self.update_task_status_done(task.id_task)
            logging.error(f"Error fetching last 100 watched for {task.task_job}")
            return "Private profile"

        last_100_watched_data = ujson.loads(last_100_watched_data)

        user_already_watched_data = set(user_already_watched_data or [])

        first_time_scrap = True if user_already_watched_data == [] else False

        new_movies_watched = [movie for movie in last_100_watched_data if movie[0] not in user_already_watched_data]

        logging.info(f"Found {len(new_movies_watched)} new movies watched")

        new_movies_watched_parsed = []

        for movie in new_movies_watched:
            #  f"https://www.filmweb.pl/api/v1/user/{task.job}/vote/film/{movie_id}"

            try:
                movie_rate_data = self.fetch(f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/film/{movie[0]}")

                if movie_rate_data is None:
                    continue

                movie_rate_data = ujson.loads(movie_rate_data)

                new_movies_watched_parsed.append(
                    filmweb.FilmWebUserWatchedMovie(
                        id_media=movie[0],
                        id_filmweb=task.task_job,
                        date=datetime.datetime.fromtimestamp(movie_rate_data["timestamp"] / 1000),
                        rate=movie_rate_data.get("rate", 0),
                        comment=movie_rate_data.get("comment", None),
                        favorite=bool(movie_rate_data.get("favorite", False)),
                    )
                )
            except Exception as e:
                logging.error(f"Error parsing movie data: {e}")
                continue

        logging.info(f"Found {len(new_movies_watched_parsed)} new movies parsed")

        if len(new_movies_watched_parsed) == 0:
            tasks.update_task_status(task.id_task, TaskStatus.DONE)
            return "No new movies"

        logging.info("Preparing to update data...")
        try:
            result = self.update_data(
                task.task_job,
                new_movies_watched_parsed,
                first_time_scrap,
                task.task_id,
            )
            logging.info("Data updated successfully.")
            return result
        except Exception as e:
            logging.error(f"Error updating data: {e}")
            return "Error updating data"

    def update_data(
        self,
        filmweb_id: str,
        movies_watched: list,
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
                        if dc_notifications.send_notification(filmweb_id=filmweb_id) is False:
                            logging.error(f"Error sending discord notification for {filmweb_id}")
                            continue
                else:
                    logging.error(f"Error updating movie data: {e}")
                    continue

            except Exception as e:
                logging.error(f"Exception while updating movie data: {e}")
                continue

        tasks.update_task_status(task_id, TaskStatus.DONE)

        return True
