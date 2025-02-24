import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import sentry_sdk
from fake_useragent import UserAgent
from sentry_sdk.integrations.logging import LoggingIntegration

from filman_crawler.tasks.scrap_movie import Scraper as movie_scrapper
from filman_crawler.tasks.scrap_series import Scraper as series_scrapper
from filman_crawler.tasks.scrap_user_watched_movies import Scraper as user_watched_movies_scrapper
from filman_crawler.tasks.scrap_user_watched_series import Scraper as user_watched_series_scrapper
from filman_server.database.schemas import Task, TaskTypes

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

CORE_ENDPOINT = os.environ.get("CORE_ENDPOINT", "http://localhost:8001")

HEADERS = {
    "User-Agent": UserAgent().random,
    "x-locale": "pl_PL",
    "Host": "www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "If-Modified-Since": "0",
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

ALLOWED_TASKS = [
    TaskTypes.SCRAP_FILMWEB_MOVIE,
    TaskTypes.SCRAP_FILMWEB_SERIES,
    TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES,
    TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES,
]

TASK_TYPES = [task for task in ALLOWED_TASKS]

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,  # Capture info and above as breadcrumbs  # Send errors as events
)


if os.environ.get("SENTRY_ENABLED", "false") == "true":
    sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), integrations=[sentry_logging])


def check_there_are_any_tasks():
    try:
        r = requests.head(
            f"{CORE_ENDPOINT}/tasks/get/to_do",
            params={"task_types": TASK_TYPES},
            headers=HEADERS,
        )

        if r.status_code != 200:
            return False

        return True

    except Exception as e:
        logging.error(f"Error checking tasks: {e}")
        return False


def get_task_to_do() -> Task:
    try:
        r = requests.get(
            f"{CORE_ENDPOINT}/tasks/get/to_do",
            params={"task_types": TASK_TYPES},
            headers=HEADERS,
            timeout=3,
        )

        if r.status_code != 200:
            return None

        task = Task(**r.json())
        logging.info(f"Fetched task: {task}")
        return task

    except Exception as e:
        logging.error(f"Error getting task to do: {e}")
        return None


def do_task(task: Task):
    if task.task_type == TaskTypes.SCRAP_FILMWEB_MOVIE:
        scraper = movie_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT, movie_id=task.task_job)
        scraper.scrap(task)

    elif task.task_type == TaskTypes.SCRAP_FILMWEB_SERIES:
        scraper = series_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT, series_id=task.task_job)
        scraper.scrap(task)

    elif task.task_type == TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES:
        scraper = user_watched_movies_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT)
        scraper.scrap(task)

    elif task.task_type == TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES:
        scraper = user_watched_series_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT)
        scraper.scrap(task)

    else:
        logging.error(f"Unknown task type: {task.task_type}")


def check_connection() -> bool:
    try:
        r = requests.get(CORE_ENDPOINT, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return True
        return False
    except Exception as e:
        logging.warning(f"Error checking connection: {e}")
        return False


def main():
    logging.info("Program started")

    wait_time = 2

    with ThreadPoolExecutor(max_workers=3) as executor:
        while True:
            logging.debug("Fetching tasks from endpoint")

            if check_there_are_any_tasks():
                task = get_task_to_do()

                if task is not None:
                    executor.submit(do_task, task)
                else:
                    logging.info("No tasks to do")
            else:
                logging.info("No tasks to do")

            time.sleep(wait_time)


if __name__ == "__main__":
    while not check_connection():
        logging.warning("Connection not established, retrying in 5 seconds")
        time.sleep(5)

    logging.info("Connection established")

    main()
