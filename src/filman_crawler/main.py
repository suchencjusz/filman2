import logging
import os
import sys
import time

import requests
import sentry_sdk
from fake_useragent import UserAgent
from sentry_sdk.integrations.logging import LoggingIntegration

from filman_crawler.tasks.scrap_movie import Scraper as movie_scrapper
from filman_crawler.tasks.scrap_series import Scraper as series_scrapper
from filman_crawler.tasks.scrap_user_watched_movies import Scraper as user_watched_movies_scrapper
from filman_crawler.tasks.scrap_user_watched_series import Scraper as user_watched_series_scrapper
from filman_crawler.tasks.utils import DEFAULT_TIMEOUT, SERVER_HEADERS, Tasks
from filman_server.database.schemas import Task, TaskStatus, TaskTypes

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

CORE_ENDPOINT = os.environ.get("CORE_ENDPOINT", "http://localhost:8001").rstrip("/")
FALLBACK_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def _build_user_agent() -> str:
    try:
        return UserAgent().random
    except Exception as exc:
        logging.warning(f"Failed to initialize fake_useragent, using fallback: {exc}")
        return FALLBACK_USER_AGENT


HEADERS = {
    "User-Agent": _build_user_agent(),
    "x-locale": "pl_PL",
    "Host": "www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
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
    level=logging.WARNING,
    event_level=logging.ERROR,  # Capture info and above as breadcrumbs  # Send errors as events
)


if os.environ.get("SENTRY_ENABLED", "false") == "true":
    sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"), integrations=[sentry_logging])

BASE_WAIT_SECONDS = 2
MAX_BACKOFF_SECONDS = 30
OUTAGE_ERROR_LOG_INTERVAL_SECONDS = 60

_server_session = requests.Session()
_filmweb_session = requests.Session()
_last_outage_error_log = 0.0


def _log_server_connection_error(message: str) -> None:
    """Rate-limit error logs during prolonged server outages to avoid Sentry event floods."""
    global _last_outage_error_log
    now = time.monotonic()
    if now - _last_outage_error_log >= OUTAGE_ERROR_LOG_INTERVAL_SECONDS:
        _last_outage_error_log = now
        logging.error(message)
    else:
        logging.warning(message)


def check_there_are_any_tasks() -> bool:
    try:
        r = _server_session.head(
            f"{CORE_ENDPOINT}/tasks/get/to_do",
            params={"task_types": TASK_TYPES},
            headers=SERVER_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        return r.status_code == 200
    except requests.RequestException as e:
        _log_server_connection_error(f"Error checking tasks: {e}")
        return False


def get_task_to_do() -> tuple[Task | None, bool]:
    """Fetch next queued task. Returns (task, server_reachable)."""
    try:
        r = _server_session.get(
            f"{CORE_ENDPOINT}/tasks/get/to_do",
            params={"task_types": TASK_TYPES},
            headers=SERVER_HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )

        if r.status_code == 404:
            return None, True

        if r.status_code != 200:
            logging.warning(f"Unexpected status getting task to do: HTTP {r.status_code}")
            return None, True

        task = Task(**r.json())
        logging.info(f"Fetched task: {task}")
        return task, True

    except requests.RequestException as e:
        _log_server_connection_error(f"Error getting task to do: {e}")
        return None, False
    except Exception as e:
        logging.error(f"Error parsing task to do: {e}")
        return None, True


def do_task(task: Task) -> None:
    tasks_client = Tasks(HEADERS, CORE_ENDPOINT, session=_server_session)
    try:
        if task.task_type == TaskTypes.SCRAP_FILMWEB_MOVIE:
            scraper = movie_scrapper(
                headers=HEADERS,
                endpoint_url=CORE_ENDPOINT,
                movie_id=task.task_job,
                session=_filmweb_session,
                server_session=_server_session,
            )
            success = scraper.scrap(task)

        elif task.task_type == TaskTypes.SCRAP_FILMWEB_SERIES:
            scraper = series_scrapper(
                headers=HEADERS,
                endpoint_url=CORE_ENDPOINT,
                series_id=task.task_job,
                session=_filmweb_session,
                server_session=_server_session,
            )
            success = scraper.scrap(task)

        elif task.task_type == TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES:
            scraper = user_watched_movies_scrapper(
                headers=HEADERS,
                endpoint_url=CORE_ENDPOINT,
                session=_filmweb_session,
                server_session=_server_session,
            )
            success = scraper.scrap(task)

        elif task.task_type == TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES:
            scraper = user_watched_series_scrapper(
                headers=HEADERS,
                endpoint_url=CORE_ENDPOINT,
                session=_filmweb_session,
                server_session=_server_session,
            )
            success = scraper.scrap(task)

        else:
            logging.error(f"Unknown task type: {task.task_type}")
            tasks_client.update_task_status(task.task_id, TaskStatus.ERROR)
            return

        if success is False:
            logging.warning(f"Task {task.task_id} ({task.task_type}) failed; marking as error")
            tasks_client.update_task_status(task.task_id, TaskStatus.ERROR)

    except Exception as exc:
        logging.exception(f"Unhandled error executing task {task.task_id} ({task.task_type}): {exc}")
        tasks_client.update_task_status(task.task_id, TaskStatus.ERROR)


def check_connection() -> bool:
    try:
        r = _server_session.get(CORE_ENDPOINT, headers=SERVER_HEADERS, timeout=5)
        return r.status_code == 200
    except requests.RequestException as e:
        logging.warning(f"Error checking connection: {e}")
        return False


def main():
    logging.info("Program started")

    wait_time = BASE_WAIT_SECONDS

    while True:
        logging.debug("Fetching tasks from endpoint")

        task, server_reachable = get_task_to_do()

        if not server_reachable:
            wait_time = min(wait_time * 2, MAX_BACKOFF_SECONDS)
            time.sleep(wait_time)
            continue

        wait_time = BASE_WAIT_SECONDS

        if task is not None:
            do_task(task)
        else:
            logging.info("No tasks to do")
            time.sleep(wait_time)


if __name__ == "__main__":
    while not check_connection():
        logging.warning("Connection not established, retrying in 5 seconds")
        time.sleep(5)

    logging.info("Connection established")

    main()
