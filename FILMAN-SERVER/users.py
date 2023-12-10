from mysql.connector.errors import IntegrityError
import requests
import ujson


from fake_useragent import UserAgent

from utils import cut_unix_timestamp_miliseconds
from db import Database
from movie import Movie, MovieManager


class User:
    def __init__(self, id_filmweb, id_discord, discord_color):
        self.id_filmweb = id_filmweb
        self.id_discord = id_discord
        self.discord_color = discord_color

    def __str__(self):
        return f"{self.id_filmweb} {self.id_discord} {self.discord_color}"


class UserManager:
    def __init__(self):
        pass

    def check_user_has_filmweb_account(self, id_filmweb: str):
        headers = {
            "User-Agent": UserAgent().random,
        }

        response = requests.head(
            f"https://www.filmweb.pl/api/v1/user/{id_filmweb}/preview", headers=headers
        )

        if response.status_code == 200:
            return True

        return False

    def create_user(self, id_filmweb: str, id_discord: int):
        db = Database()

        if self.check_user_has_filmweb_account(id_filmweb) is False:
            return "User does not exist on filmweb"

        try:
            db.cursor.execute(
                f"INSERT INTO users (id_filmweb, id_discord) VALUES (%s, %s)",
                (id_filmweb, id_discord),
            )

            db.connection.commit()
        except IntegrityError:
            return "User already exists"

        db.connection.close()

        return True

    def delete_user(self, id_filmweb: str):
        db = Database()

        db.cursor.execute(
            f"DELETE FROM users WHERE id_filmweb = %s",
            (id_filmweb,),
        )

        db.connection.commit()
        db.connection.close()

        return True
