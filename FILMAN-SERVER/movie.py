import requests
import ujson

from fake_useragent import UserAgent

from db import Database


class Movie:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.year = kwargs.get("year")
        self.poster_uri = kwargs.get(
            "poster_uri"
        )  # https://fwcdn.pl/fpo/20/32/32032/6933343.$.jpg

    def __str__(self):
        return f"{self.title} ({self.year})"


class MovieManager:
    def __init__(self):
        pass

    def __scrap_movie_by_id(self, id):
        ua = UserAgent()
        headers = {"User-Agent": ua.random}

        response = requests.get(
            f"https://www.filmweb.pl/api/v1/title/{id}/info", headers=headers
        )

        if response.status_code == 200:
            data = ujson.loads(response.content)
            return Movie(
                id=id,
                title=data.get("title"),
                year=int(data.get("year", 0)),
                poster_uri=data.get("posterPath"),
            )

        return None

    def __add_movie_to_db(self, movie):
        db = Database()
        db.cursor.execute(
            f"INSERT INTO movies (id, title, year, poster_uri) VALUES ({movie.id}, '{movie.title}', {movie.year}, '{movie.poster_uri}')"
        )
        db.connection.commit()
        db.connection.close()

    def get_movie_by_id(self, id):
        db = Database()
        db.cursor.execute(f"SELECT * FROM movies WHERE id = {id}")
        result = db.cursor.fetchone()
        db.connection.close()

        if result is None:
            movie = self.__scrap_movie_by_id(id)
            if movie is not None:
                self.__add_movie_to_db(movie)
                return movie
            else:
                return None
        else:
            return Movie(
                id=result[0], title=result[1], year=result[2], poster_uri=result[3]
            )
