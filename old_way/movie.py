# import time

# from db import Database
# from tasks import TasksManager


# class Movie:
#     def __init__(self, **kwargs):
#         self.id = kwargs.get("id")
#         self.title = kwargs.get("title")
#         self.year = kwargs.get("year")
#         self.poster_uri = kwargs.get("poster_uri")
#         self.community_rate = kwargs.get("community_rate")

#     def __str__(self):
#         return f"{self.title} ({self.year})"


# class MovieManager:
#     def __init__(self):
#         pass

#     def add_movie_to_db(self, movie):
#         db = Database()

#         db.cursor.execute(f"SELECT * FROM movies WHERE id = %s", (movie.id,))

#         result = db.cursor.fetchone()

#         if result is None:
#             db.cursor.execute(
#                 f"INSERT INTO movies (id, updated_unixtime, title, year, poster_uri, community_rate) VALUES (%s, %s, %s, %s, %s, %s)",
#                 (
#                     movie.id,
#                     int(time.time()),
#                     movie.title,
#                     movie.year,
#                     movie.poster_uri,
#                     movie.community_rate,
#                 ),
#             )

#             db.connection.commit()
#             db.connection.close()

#             return True

#         db.cursor.execute(
#             f"UPDATE movies SET updated_unixtime = %s, title = %s, year = %s, poster_uri = %s, community_rate = %s WHERE id = %s",
#             (
#                 int(time.time()),
#                 movie.title,
#                 movie.year,
#                 movie.poster_uri,
#                 movie.community_rate,
#                 movie.id,
#             ),
#         )

#         db.connection.commit()
#         db.connection.close()

#         return True

#     def get_movie_by_id(self, id):
#         db = Database()
#         db.cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
#         result = db.cursor.fetchone()
#         db.connection.close()

#         if result is None:
#             task_manager = TasksManager()
#             task_manager.new_task("scrap_movie", id)

#             return None
#         else:
#             return Movie(
#                 id=result[0],
#                 title=result[2],
#                 year=result[3],
#                 poster_uri=result[4],
#                 community_rate=result[5],
#             )
