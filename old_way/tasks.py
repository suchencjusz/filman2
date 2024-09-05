# import time
# from datetime import datetime, timedelta

# from users import UserManager
# from db import Database


# class Task:
#     def __init__(
#         self, id_task, status, type, job, unix_timestamp, unix_timestamp_last_update
#     ):
#         self.id_task = id_task
#         self.status = status
#         self.type = type
#         self.job = job
#         self.unix_timestamp = unix_timestamp
#         self.unix_timestamp_last_update = unix_timestamp_last_update

#     def __str__(self):
#         return (
#             f"{self.id_task} {self.status} {self.type} {self.job} {self.unix_timestamp}"
#         )


# # status: waiting, in_progress, done, failed
# # type: scrap_movie, scrape_series, send_discord, check_user_new_movies, check_user_new_series


# class TasksManager:
#     def __init__(self):
#         pass

#     def update_stuck_tasks(self):
#         db = Database()

#         # Get the current time
#         now = datetime.now()

#         # Calculate the threshold for 'stuck' tasks
#         threshold = now - timedelta(minutes=5)  # adjust as needed

#         # Convert the threshold to a Unix timestamp
#         threshold_timestamp = int(threshold.timestamp())

#         # Get all tasks with a status of 'in_progress' and a unix_timestamp_last_update older than the threshold
#         db.cursor.execute(
#             f"UPDATE tasks SET status = %s WHERE status = %s AND unix_timestamp_last_update < %s",
#             ("waiting", "in_progress", threshold_timestamp),
#         )

#         db.connection.commit()
#         db.connection.close()

#         return True

#     def delete_old_tasks(self):
#         db = Database()

#         # Get the current time
#         now = datetime.now()

#         # Calculate the threshold for 'stuck' tasks
#         threshold = now - timedelta(minutes=30)

#         # Convert the threshold to a Unix timestamp
#         threshold_timestamp = int(threshold.timestamp())

#         # Get all tasks with a status of 'in_progress' and a unix_timestamp_last_update older than the threshold
#         db.cursor.execute(
#             f"DELETE FROM tasks WHERE unix_timestamp_last_update < %s",
#             (threshold_timestamp,),
#         )
#         db.connection.commit()
#         db.connection.close()

#         return True

#     def update_task_status(self, id_task: int, status: str):
#         db = Database()

#         if status == "done":
#             self.delete_task(id_task)

#         db.cursor.execute(
#             f"UPDATE tasks SET status = %s WHERE id_task = %s",
#             (status, id_task),
#         )

#         db.connection.commit()
#         db.connection.close()

#         return True

#     def delete_task(self, id_task: int):
#         db = Database()

#         db.cursor.execute(
#             f"DELETE FROM tasks WHERE id_task = %s",
#             (id_task,),
#         )

#         db.connection.commit()
#         db.connection.close()

#         return True

#     def add_scrap_users_task(self):
#         db = Database()

#         user_manager = UserManager()

#         all_users = user_manager.get_all_users_from_db()

#         for user in all_users:
#             self.new_task("check_user_new_movies", user.id_filmweb)
#             self.new_task("check_user_new_series", user.id_filmweb)

#         return True

#     def add_scrap_movies_task(self):
#         db = Database()

#         db.cursor.execute("SELECT id FROM movies")
#         result = db.cursor.fetchall()

#         for movie in result:
#             self.new_task("scrap_movie", movie[0])

#         return True

#     def add_scrap_series_task(self):
#         db = Database()

#         db.cursor.execute("SELECT id FROM series")
#         result = db.cursor.fetchall()

#         for series in result:
#             self.new_task("scrap_series", series[0])

#         return True

#     def new_task(self, type: str, job: str):
#         # status: waiting, in_progress, done, failed
#         # type: scrap_movie, scrape_series, send_discord, check_user_new_movies, check_user_new_series,

#         db = Database()

#         unix_timestamp = int(time.time())

#         db.cursor.execute(
#             f"INSERT INTO tasks (status, type, job, unix_timestamp, unix_timestamp_last_update) VALUES (%s, %s, %s, %s, %s)",
#             ("waiting", type, job, unix_timestamp, unix_timestamp),
#         )

#         db.connection.commit()
#         db.connection.close()

#         return True

#     def get_and_update_tasks(self, types: list = None, status: str = "waiting"):
#         db = Database()

#         types_placeholder = ", ".join(["%s"] * len(types))

#         db.cursor.execute(
#             f"SELECT * FROM tasks WHERE type IN ({types_placeholder}) AND status = %s ORDER BY id_task ASC LIMIT 5",
#             (*types, status),
#         )

#         result = db.cursor.fetchall()

#         if result is None:
#             return None

#         tasks = []

#         for task in result:
#             tasks.append(
#                 Task(
#                     id_task=task[0],
#                     status=task[1],
#                     type=task[2],
#                     job=task[3],
#                     unix_timestamp=task[4],
#                     unix_timestamp_last_update=task[5],
#                 )
#             )

#         for task in tasks:
#             db.cursor.execute(
#                 f"UPDATE tasks SET status = %s WHERE id_task = %s",
#                 ("in_progress", task.id_task),
#             )

#         db.connection.commit()
#         db.connection.close()

#         return tasks

#     def get_tasks_count_by_type_and_status(self, type: str, status: str):
#         db = Database()

#         db.cursor.execute(
#             f"SELECT COUNT(*) FROM tasks WHERE type = %s AND status = %s",
#             (type, status),
#         )

#         result = db.cursor.fetchone()

#         db.connection.commit()
#         db.connection.close()

#         return result[0]

#     def get_task_by_type(self, type: str):
#         db = Database()

#         if type is None:
#             db.cursor.execute(
#                 f"SELECT * FROM tasks WHERE status = %s ORDER BY id_task ASC LIMIT 1",
#                 ("waiting",),
#             )
#         else:
#             db.cursor.execute(
#                 f"SELECT * FROM tasks WHERE type = %s AND status = %s ORDER BY id_task ASC LIMIT 1",
#                 (type, "waiting"),
#             )

#         result = db.cursor.fetchone()

#         if result is None:
#             return None

#         task = Task(
#             id_task=result[0],
#             status=result[1],
#             type=result[2],
#             job=result[3],
#             unix_timestamp=result[4],
#             unix_timestamp_last_update=result[5],
#         )

#         return task

#         # db.cursor.execute(
#         #     f"UPDATE tasks SET status = %s WHERE id_task = %s",
#         #     ("in_progress", task.id_task),
#         # )

#         # db.connection.commit()
#         # db.connection.close()

#     def reset_stuck_tasks():
#         db = Database()

#         # Get the current time
#         now = datetime.now()

#         # Calculate the threshold for 'stuck' tasks
#         threshold = now - timedelta(minutes=5)  # adjust as needed

#         # Convert the threshold to a Unix timestamp
#         threshold_timestamp = int(threshold.timestamp())

#         # Get all tasks with a status of 'in_progress' and a unix_timestamp_last_update older than the threshold
#         db.cursor.execute(
#             f"SELECT * FROM tasks WHERE status = 'in_progress' AND unix_timestamp_last_update < %s",
#             (threshold_timestamp,),
#         )
#         tasks = db.cursor.fetchall()

#         for task in tasks:
#             # Update the status of the task back to 'in_progress'
#             db.cursor.execute(
#                 f"UPDATE tasks SET status = 'in_progress' WHERE id_task = %s",
#                 (task["id_task"],),
#             )

#         db.connection.commit()
#         db.connection.close()
