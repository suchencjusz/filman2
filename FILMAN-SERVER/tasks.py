import requests
import ujson
import time

from mysql.connector.errors import IntegrityError
from fake_useragent import UserAgent
from datetime import datetime, timedelta

from db import Database


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


# status: waiting, in_progress, done, failed
# type: scrap_movie, scrape_series, send_discord, check_user_new_movies, check_user_new_series


class TaskManager:
    def __init__(self):
        pass

    def update_task_status(self, id_task: int, status: str):
        db = Database()

        if status == "done":
            self.delete_task(id_task)

        db.cursor.execute(
            f"UPDATE tasks SET status = %s WHERE id_task = %s",
            (status, id_task),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def delete_task(self, id_task: int):
        db = Database()

        db.cursor.execute(
            f"DELETE FROM tasks WHERE id_task = %s",
            (id_task,),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def new_task(self, type: str, job: str):
        # status: waiting, in_progress, done, failed
        # type: scrap_movie, scrape_series, send_discord, check_user_new_movies, check_user_new_series

        db = Database()

        unix_timestamp = int(time.time())

        db.cursor.execute(
            f"INSERT INTO tasks (status, type, job, unix_timestamp, unix_timestamp_last_update) VALUES (%s, %s, %s, %s, %s)",
            ("waiting", type, job, unix_timestamp, unix_timestamp),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def get_tasks_count_by_type_and_status(self, type: str, status: str):
        db = Database()

        db.cursor.execute(
            f"SELECT COUNT(*) FROM tasks WHERE type = %s AND status = %s",
            (type, status),
        )

        result = db.cursor.fetchone()

        db.connection.commit()
        db.connection.close()

        return result[0]

    def get_task_by_type(self, type: str):
        db = Database()

        db.cursor.execute(
            f"SELECT * FROM tasks WHERE type = %s AND status = %s",
            (type, "waiting"),
        )
        result = db.cursor.fetchone()

        if result is None:
            return None

        task = Task(
            id_task=result[0],
            status=result[1],
            type=result[2],
            job=result[3],
            unix_timestamp=result[4],
            unix_timestamp_last_update=result[5],
        )

        yield task

        db.cursor.execute(
            f"UPDATE tasks SET status = %s WHERE id_task = %s",
            ("in_progress", task.id_task),
        )

        db.connection.commit()
        db.connection.close()

    def reset_stuck_tasks():
        db = Database()

        # Get the current time
        now = datetime.now()

        # Calculate the threshold for 'stuck' tasks
        threshold = now - timedelta(minutes=5)  # adjust as needed

        # Convert the threshold to a Unix timestamp
        threshold_timestamp = int(threshold.timestamp())

        # Get all tasks with a status of 'in_progress' and a unix_timestamp_last_update older than the threshold
        db.cursor.execute(
            f"SELECT * FROM tasks WHERE status = 'in_progress' AND unix_timestamp_last_update < %s",
            (threshold_timestamp,),
        )
        tasks = db.cursor.fetchall()

        for task in tasks:
            # Update the status of the task back to 'in_progress'
            db.cursor.execute(
                f"UPDATE tasks SET status = 'in_progress' WHERE id_task = %s",
                (task["id_task"],),
            )

        db.connection.commit()
        db.connection.close()
