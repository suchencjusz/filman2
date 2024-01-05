import os
import requests
import ujson
import time
import logging

from fake_useragent import UserAgent

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


from tasks.scrap_movie import Scraper as movie_scrapper
from tasks.scrap_series import Scraper as series_scrapper
from tasks.scrap_user_watched_movies import Scraper as user_watched_movies_scrapper
from tasks.scrap_user_watched_series import Scraper as user_watched_series_scrapper

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


class TaskTypes(str, Enum):
    SCRAP_USER = "scrap_user"
    SCRAP_FILMWEB_MOVIE = "scrap_filmweb_movie"
    SCRAP_FILMWEB_SERIES = "scrap_filmweb_series"
    SCRAP_FILMWEB_USER_WATCHED_MOVIES = "scrap_filmweb_user_watched_movies"
    SCRAP_FILMWEB_USER_WATCHED_SERIES = "scrap_filmweb_user_watched_series"
    SEND_DISCORD_NOTIFICATION = "send_discord_notification"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class Task(BaseModel):
    task_id: int
    task_status: TaskStatus
    task_type: TaskTypes
    task_job: str
    task_created: datetime
    task_started: Optional[datetime] = None
    task_finished: Optional[datetime] = None


ALLOWED_TASKS = [
    TaskTypes.SCRAP_FILMWEB_MOVIE,
    TaskTypes.SCRAP_FILMWEB_SERIES,
    TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES,
    TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES,
]

TASK_TYPES = [task for task in ALLOWED_TASKS]


def check_there_are_any_tasks():
    try:
        r = requests.head(
            f"{CORE_ENDPOINT}/tasks/get/task/to_do",
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
            f"{CORE_ENDPOINT}/tasks/get/task/to_do",
            params={"task_types": TASK_TYPES},
            headers=HEADERS,
        )

        if r.status_code != 200:
            return None
        
        return Task(**r.json())
    
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
        scraper = user_watched_movies_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT, user_id=task.task_job)
        scraper.scrap(task)

    elif task.task_type == TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES:
        scraper = user_watched_series_scrapper(headers=HEADERS, endpoint_url=CORE_ENDPOINT, user_id=task.task_job)
        scraper.scrap(task)

    else:
        logging.error(f"Unknown task type: {task.task_type}")


    

def main():
    logging.info("Program started")

    min_wait = 2   # Minimum wait time in seconds
    max_wait = 60  # Maximum wait time in seconds
    wait_time = min_wait

    with ThreadPoolExecutor() as executor:
        while True:
            logging.info("Fetching tasks from endpoint")

            if check_there_are_any_tasks():
                task = get_task_to_do()

                if task is not None:
                    executor.submit(do_task, task)
                    wait_time = min_wait
                else:
                    logging.info("No tasks found")
                    wait_time = min_wait

            time.sleep(wait_time) 

if __name__ == "__main__":
    main()
