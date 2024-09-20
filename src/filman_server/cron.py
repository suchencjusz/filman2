import logging
import time
from threading import Thread

import requests
import schedule

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class Cron:
    def __init__(self):
        self.schedule = schedule

    # scrap user watched movies task
    @staticmethod
    def tasks_new_scrap_filmweb_users_movies():
        response = requests.get("http://localhost:8000/tasks/new/scrap/filmweb/users/movies", timeout=5)
        logging.info(f"Executed tasks_new_scrap_filmweb_users_movies: {response.status_code}")

    # scrap movies task
    @staticmethod
    def tasks_new_scrap_filmweb_movies():
        response = requests.get("http://localhost:8000/tasks/new/scrap/filmweb/movies", timeout=5)
        logging.info(f"Executed tasks_new_scrap_filmweb_movies: {response.status_code}")

    # update stuck tasks
    @staticmethod
    def tasks_update_stuck_tasks():
        response = requests.get("http://localhost:8000/tasks/update/stuck/5", timeout=5)
        logging.info(f"Executed tasks_update_stuck_tasks: {response.status_code}")

    # update old tasks
    @staticmethod
    def tasks_update_old_tasks():
        response = requests.get("http://localhost:8000/tasks/update/old/20", timeout=5)
        logging.info(f"Executed tasks_update_old_tasks: {response.status_code}")

    def schedule_tasks(self):
        self.schedule.every(3).minutes.do(self.tasks_new_scrap_filmweb_users_movies)
        self.schedule.every(6).hours.do(self.tasks_new_scrap_filmweb_movies)
        self.schedule.every(5).minutes.do(self.tasks_update_stuck_tasks)
        self.schedule.every(20).minutes.do(self.tasks_update_old_tasks)

        while True:
            self.schedule.run_pending()
            time.sleep(1)

    def start(self):
        scheduler_thread = Thread(target=self.schedule_tasks)
        scheduler_thread.start()
