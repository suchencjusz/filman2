import logging
import os
import time
from threading import Thread

import requests
import schedule

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class Cron:

    def __init__(self):
        self.schedule = schedule

    @staticmethod
    def execute_task(url, task_name):
        try:
            response = requests.get(url, timeout=10)
            logging.info(f"Executed {task_name}: {response.status_code}")
        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while executing {task_name}")
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while executing {task_name}: {e}")

    @staticmethod
    def tasks_new_scrap_filmweb_users_series():
        Cron.execute_task(
            "http://localhost:8000/tasks/new/scrap/filmweb/users/series",
            "tasks_new_scrap_filmweb_users_series",
        )

    @staticmethod
    def tasks_new_scrap_filmweb_series():
        Cron.execute_task(
            "http://localhost:8000/tasks/new/scrap/filmweb/series",
            "tasks_new_scrap_filmweb_series",
        )

    @staticmethod
    def tasks_new_scrap_filmweb_users_movies():
        Cron.execute_task(
            "http://localhost:8000/tasks/new/scrap/filmweb/users/movies",
            "tasks_new_scrap_filmweb_users_movies",
        )

    @staticmethod
    def tasks_new_scrap_filmweb_movies():
        Cron.execute_task(
            "http://localhost:8000/tasks/new/scrap/filmweb/movies",
            "tasks_new_scrap_filmweb_movies",
        )

    @staticmethod
    def tasks_update_stuck_tasks():
        Cron.execute_task("http://localhost:8000/tasks/update/stuck/5", "tasks_update_stuck_tasks")

    @staticmethod
    def tasks_update_old_tasks():
        Cron.execute_task("http://localhost:8000/tasks/update/old/20", "tasks_update_old_tasks")

    def schedule_tasks(self):
        # filmweb series
        self.schedule.every(3).minutes.do(self.tasks_new_scrap_filmweb_users_series)
        self.schedule.every(6).hours.do(self.tasks_new_scrap_filmweb_series)

        # filmweb movies
        self.schedule.every(3).minutes.do(self.tasks_new_scrap_filmweb_users_movies)
        self.schedule.every(6).hours.do(self.tasks_new_scrap_filmweb_movies)

        # tasks mgmt
        self.schedule.every(5).minutes.do(self.tasks_update_stuck_tasks)
        self.schedule.every(20).minutes.do(self.tasks_update_old_tasks)

        while True:
            self.schedule.run_pending()
            time.sleep(1)

    def start(self):
        scheduler_thread = Thread(target=self.schedule_tasks)
        scheduler_thread.start()
