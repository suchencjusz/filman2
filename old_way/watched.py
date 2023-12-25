# from db import Database
# from movie import Movie, MovieManager
# from series import Series, SeriesManager
# from tasks import TasksManager
# from users import UserManager
# from discord_m import DiscordManager


# class Watched:
#     def __init__(
#         self, id_watched, id_filmweb, movie_id, rate, comment, favorite, unix_timestamp
#     ):
#         self.id_watched = id_watched
#         self.id_filmweb = id_filmweb
#         self.movie_id = movie_id
#         self.rate = rate
#         self.comment = comment
#         self.favorite = favorite
#         self.unix_timestamp = unix_timestamp

#     def __str__(self):
#         return f"{self.id_watched} {self.id_filmweb} {self.movie_id} {self.rate} {self.comment} {self.favourite} {self.unix_timestamp}"


# class WatchedManager:
#     def __init__(self):
#         pass

#     def update_movie_data(
#         self,
#         movie_id: int,
#         title: str,
#         year: int,
#         poster_path: str,
#         community_rate: float,
#     ):
#         movie_manager = MovieManager()

#         movie = movie_manager.get_movie_by_id(movie_id)

#         if movie is None:
#             return False

#         movie.title = title
#         movie.year = year
#         movie.poster_path = poster_path
#         movie.community_rate = community_rate

#         movie_manager.update_movie(movie)

#         return True

#     def add_watched_series(
#         self,
#         id_filmweb: str,
#         series_id: int,
#         rate: int,
#         comment: str,
#         favorite: bool,
#         unix_timestamp: int,
#         without_discord: bool,
#     ):
#         db = Database()
#         series_manager = SeriesManager()

#         # check series is in db
#         db.cursor.execute(f"SELECT * FROM series WHERE id = %s", (series_id,))
#         result = db.cursor.fetchone()

#         if result is None:
#             # if not, create task to scrap series

#             series_manager.add_series_to_db(
#                 Series(
#                     id=series_id,
#                     title="",
#                     year=0,
#                     other_year=0,
#                     poster_uri="",
#                     community_rate=0,
#                 )
#             )

#             task_manager = TasksManager()
#             task_manager.new_task("scrap_series", series_id)

#         # check it is not already in watched
#         db.cursor.execute(
#             f"SELECT * FROM watched_series WHERE id_filmweb = %s AND series_id = %s",
#             (id_filmweb, series_id),
#         )

#         result = db.cursor.fetchone()

#         if result is not None:
#             print("Already watched")
#             return "Already watched"
        
#         # add to watched
#         db.cursor.execute(
#             f"INSERT INTO watched_series (id_filmweb, series_id, rate, comment, favourite, unix_timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
#             (id_filmweb, series_id, rate, comment, favorite, unix_timestamp),
#         )

#         db.connection.commit()
#         db.connection.close()

#         if without_discord is True:
#             return True
        
#         task_manager = TasksManager()
#         task_manager.new_task("send_discord", f"{id_filmweb},{series_id}")

#         return True
        
#     def add_watched_movie(
#         self,
#         id_filmweb: str,
#         movie_id: int,
#         rate: int,
#         comment: str,
#         favorite: bool,
#         unix_timestamp: int,
#         without_discord: bool,
#     ):
#         db = Database()
#         movie_manager = MovieManager()

#         # check movie is in db
#         db.cursor.execute(f"SELECT * FROM movies WHERE id = %s", (movie_id,))
#         result = db.cursor.fetchone()

#         if result is None:
#             # if not, create task to scrap movie

#             movie_manager.add_movie_to_db(
#                 Movie(
#                     id=movie_id,
#                     title="",
#                     year=0,
#                     poster_uri="",
#                     community_rate=0,
#                 )
#             )

#             task_manager = TasksManager()
#             task_manager.new_task("scrap_movie", movie_id)

#         # check it is not already in watched
#         db.cursor.execute(
#             f"SELECT * FROM watched_movies WHERE id_filmweb = %s AND movie_id = %s",
#             (id_filmweb, movie_id),
#         )

#         result = db.cursor.fetchone()

#         if result is not None:
#             print("Already watched")
#             return "Already watched"

#         # add to watched
#         db.cursor.execute(
#             f"INSERT INTO watched_movies (id_filmweb, movie_id, rate, comment, favourite, unix_timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
#             (id_filmweb, movie_id, rate, comment, favorite, unix_timestamp),
#         )
#         db.connection.commit()
#         db.connection.close()

#         if without_discord is True:
#             return True

#         task_manager = TasksManager()
#         task_manager.new_task("send_discord", f"{id_filmweb},{movie_id}")

#         return True

#     def get_all_watched_movies(self, id_filmweb: str):
#         db = Database()
#         db.cursor.execute(
#             f"SELECT * FROM watched_movies WHERE id_filmweb = %s", (id_filmweb,)
#         )
#         result = db.cursor.fetchall()
#         db.connection.close()

#         if result is None:
#             return None

#         if len(result) == 0:
#             return None

#         watched_movies = []

#         for row in result:
#             watched_movies.append(
#                 Watched(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
#             )

#         return watched_movies

#     def get_watched_movie_with_rates(self, id_filmweb: str, movie_id: int):
#         db = Database()
#         db.cursor.execute(
#             f"SELECT * FROM watched_movies WHERE id_filmweb = %s AND movie_id = %s",
#             (id_filmweb, movie_id),
#         )

#         result = db.cursor.fetchone()

#         w = Watched(
#             result[0], result[1], result[2], result[3], result[4], result[5], result[6]
#         )

#         db.connection.close()

#         movie_manager = MovieManager()
#         user_manager = UserManager()
#         discord_manager = DiscordManager()

#         return (
#             w,
#             movie_manager.get_movie_by_id(movie_id),
#             user_manager.get_user_by_filmweb_id(id_filmweb),
#             discord_manager.get_user_notification_destinations(id_filmweb),
#         )
