from mysql.connector.errors import IntegrityError
import requests

from fake_useragent import UserAgent

from db import Database


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

    def get_all_users_from_db(self):
        db = Database()
        db.cursor.execute(f"SELECT * FROM users")
        result = db.cursor.fetchall()
        db.connection.close()

        if result is None:
            return None

        return list(
            map(
                lambda x: User(
                    id_filmweb=x[0],
                    id_discord=x[1],
                    discord_color=x[2],
                ),
                result,
            )
        )

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
        from tasks import TasksManager

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

        tasks_manager = TasksManager()
        tasks_manager.new_task(
            "check_user_new_movies",
            f"{id_filmweb}",
        )

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

    def get_user_by_filmweb_id(self, id_filmweb: str):
        db = Database()
        db.cursor.execute(f"SELECT * FROM users WHERE id_filmweb = %s", (id_filmweb,))
        result = db.cursor.fetchone()
        db.connection.close()

        if result is None:
            return None

        return User(
            id_filmweb=result[0],
            id_discord=result[1],
            discord_color=result[2],
        )
