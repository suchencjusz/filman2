import os
import requests
import ujson
import time
import logging

from fake_useragent import UserAgent

from tasks.scrap_movie import Scraper as movie_scrapper
from tasks.scrap_user_watched import Scraper as user_watched_scrapper


from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler("app.log")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
f_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

CORE_ENDPOINT = os.environ.get("CORE_ENDPOINT", "http://localhost:8000")
# CORE_ENDPOINT = "http://localhost:8000"

HEADERS = {
    "User-Agent": UserAgent().random,
    "x-locale": "pl_PL",
    "Host": "www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.filmweb.pl",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
}

# status: waiting, in_progress, done, failed
# type: scrap_movie, scrape_series, -send_discord-, check_user_new_movies, check_user_new_series,


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


def fetch_tasks_from_endpoint():
    # r = requests.get(
    #     f'{CORE_ENDPOINT}/tasks/get?status=waiting&types=["scrap_movie","check_user_new_movies"]'
    # )

    allowed_tasks = [
        "scrap_movie",
        "check_user_new_movies",
    ]

    try:
        r = requests.post(
            f"{CORE_ENDPOINT}/tasks/get",
            json={
                "status": "waiting",
                "types": allowed_tasks,
            },
        )
    except Exception as e:
        logging.error(f"Error fetching tasks: {e}")
        return None

    if r.status_code != 200:
        logging.error(f"Error fetching tasks: HTTP {r.status_code}")
        return None

    return ujson.loads(r.text)


def main():
    logging.info("Program started")

    min_wait = 1  # Minimum wait time in seconds
    max_wait = 60  # Maximum wait time in seconds
    wait_time = min_wait

    with ThreadPoolExecutor() as executor:
        while True:
            logging.info("Fetching tasks from endpoint")
            tasks = fetch_tasks_from_endpoint()

            if tasks:
                logging.info(f"Found {len(tasks)} tasks")
                wait_time = min_wait

                for task in tasks:
                    task = Task(
                        task["id_task"],
                        task["status"],
                        task["type"],
                        task["job"],
                        task["unix_timestamp"],
                        task["unix_timestamp_last_update"],
                    )

                    if task.type == "scrap_movie":
                        m_scraper = movie_scrapper(
                            headers=HEADERS,
                            movie_id=task.job,
                            endpoint_url=CORE_ENDPOINT,
                        )
                        executor.submit(m_scraper.scrap, task)

                    if task.type == "check_user_new_movies":
                        m_scraper = user_watched_scrapper(
                            headers=HEADERS,
                            movie_id=task.job,
                            endpoint_url=CORE_ENDPOINT,
                        )
                        executor.submit(m_scraper.scrap, task)

            else:
                logging.info("No tasks found")
                wait_time = min(wait_time * 2, max_wait)

            logging.info(f"Waiting for {wait_time} seconds")
            time.sleep(wait_time)


if __name__ == "__main__":
    main()
