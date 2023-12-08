import requests
import ujson

from mysql.connector.errors import IntegrityError
from fake_useragent import UserAgent

from utils import cut_unix_timestamp_miliseconds
from db import Database
from movie import Movie, MovieManager
from tasks import TaskManager


class Watched:
    def __init__(
        self, id_watched, id_filmweb, movie_id, rate, comment, favourite, unix_timestamp
    ):
        self.id_watched = id_watched
        self.id_filmweb = id_filmweb
        self.movie_id = movie_id
        self.rate = rate
        self.comment = comment
        self.favourite = favourite
        self.unix_timestamp = unix_timestamp

    def __str__(self):
        return f"{self.id_watched} {self.id_filmweb} {self.movie_id} {self.rate} {self.comment} {self.favourite} {self.unix_timestamp}"


class WatchedManager:
    def __init__(self):
        pass

    def update_movie_data(
        self,
        movie_id: int,
        title: str,
        year: int,
        poster_path: str,
        community_rate: float,
    ):
        movie_manager = MovieManager()

        movie = movie_manager.get_movie_by_id(movie_id)

        if movie is None:
            return False

        movie.title = title
        movie.year = year
        movie.poster_path = poster_path
        movie.community_rate = community_rate

        movie_manager.update_movie(movie)

        return True

    def add_watched_movie(
        self,
        id_filmweb: str,
        movie_id: int,
        rate: int,
        comment: str,
        favourite: bool,
        unix_timestamp: int,
    ):
        db = Database()
        movie_manager = MovieManager()

        # check movie is in db
        db.cursor.execute(f"SELECT * FROM movies WHERE id = %s", (movie_id,))
        result = db.cursor.fetchone()

        if result is None:
            # if not, create task to scrap movie

            movie_manager.add_movie_to_db(
                Movie(
                    movie_id,
                    None,
                    None,
                    None,
                    None,
                )
            )

            task_manager = TaskManager()
            task_manager.new_task("scrap_movie", movie_id)

            return False

        # check it is not already in watched
        db.cursor.execute(
            f"SELECT * FROM watched_movies WHERE id_filmweb = %s AND movie_id = %s",
            (id_filmweb, movie_id),
        )

        result = db.cursor.fetchone()

        if result is not None:
            return "Already watched"

        # add to watched
        db.cursor.execute(
            f"INSERT INTO watched_movies (id_filmweb, movie_id, rate, comment, favourite, unix_timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (id_filmweb, movie_id, rate, comment, favourite, unix_timestamp),
        )
        db.connection.commit()
        db.connection.close()
        
        return True

    def get_all_watched_movie(self, id_filmweb: str):
        db = Database()
        db.cursor.execute(
            f"SELECT * FROM watched_movies WHERE id_filmweb = %s", (id_filmweb,)
        )
        result = db.cursor.fetchall()
        db.connection.close()

        if result is None:
            return None

        watched_movies = []

        for row in result:
            watched_movies.append(
                Watched(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            )

        return watched_movies
