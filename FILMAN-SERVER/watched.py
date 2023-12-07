import requests
import ujson

from mysql.connector.errors import IntegrityError
from fake_useragent import UserAgent

from utils import cut_unix_timestamp_miliseconds
from db import Database
from movie import Movie, MovieManager


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

    def add_watched_movie(
        self,
        id_filmweb: str,
        movie_id: int,
        rate: int,
        comment: str,
        favourite: bool,
        unix_timestamp: int,
    ):
        movie_manager = MovieManager()

        watched_movie = movie_manager.get_movie_by_id(movie_id)

        if watched_movie is None:
            return False

        unix_timestamp = cut_unix_timestamp_miliseconds(unix_timestamp)

        db = Database()

        # Check if movie is already in watched_movies table
        db.cursor.execute(
            f"SELECT * FROM watched_movies WHERE id_filmweb = %s AND movie_id = %s",
            (id_filmweb, movie_id),
        )
        result = db.cursor.fetchone()

        if result:
            return "Movie is already watched"

        # If movie is not watched, add it to watched_movies table
        db.cursor.execute(
            f"INSERT INTO watched_movies (id_filmweb, movie_id, rate, comment, favourite, unix_timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (id_filmweb, movie_id, rate, comment, favourite, unix_timestamp),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def get_all_watched_movie(self, id_filmweb: str):
        db = Database()
        db.cursor.execute(f"SELECT * FROM watched WHERE id_filmweb = {id_filmweb}")
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
