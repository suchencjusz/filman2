from mysql.connector.errors import IntegrityError

from db import Database

from tasks import TasksManager


class DiscordUser:
    def __init__(self, id_filmweb, id_discord, discord_color):
        self.id_filmweb = id_filmweb
        self.id_discord = id_discord
        self.discord_color = discord_color

    def __str__(self):
        return f"{self.id_filmweb} {self.id_discord} {self.discord_color}"


class DiscordGuild:
    def __init__(self, id, guild_id, channel_id):
        self.id = id
        self.guild_id = guild_id
        self.channel_id = channel_id

    def __str__(self):
        return f"{self.id} {self.guild_id} {self.channel_id}"


class DiscordManager:
    def __init__(self) -> None:
        pass

    def check_user_is_in_db(self, id_discord: int):
        db = Database()

        db.cursor.execute(
            f"SELECT * FROM users WHERE id_discord = %s",
            (id_discord,),
        )

        result = db.cursor.fetchone()

        db.connection.close()

        return result

    def get_user_notification_destinations(self, id_filmweb: str):
        db = Database()

        db.cursor.execute(
            f"SELECT discord_guilds.guild_id, discord_guilds.channel_id FROM discord_guilds, discord_destinations WHERE discord_guilds.guild_id = discord_destinations.id_guild AND discord_destinations.id_filmweb = %s",
            (id_filmweb,),
        )

        result = db.cursor.fetchall()

        db.connection.close()

        return result

    def get_user_guilds(self, id_filmweb: str):
        db = Database()

        db.cursor.execute(
            f"SELECT * FROM discord_destinations WHERE id_filmweb = %s",
            (id_filmweb,),
        )

        result = db.cursor.fetchall()

        db.connection.close()

        return result

    def delete_user_from_db(self, id_discord: int):
        db = Database()

        db.cursor.execute(
            f"DELETE FROM users WHERE id_discord = %s",
            (id_discord,),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def delete_user_from_all_guilds(self, id_filmweb: str):
        db = Database()

        db.cursor.execute(
            f"DELETE FROM discord_destinations WHERE id_filmweb = %s",
            (id_filmweb,),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def delete_user_from_guild(self, id_discord: int, guild_id: int):
        db = Database()

        db.cursor.execute(
            "DELETE FROM discord_destinations WHERE id_filmweb = (SELECT id_filmweb FROM users WHERE id_discord = %s) AND guild_id = %s",
            (id_discord, guild_id),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def delete_user_from_all_destinations(self, id_discord: int):
        db = Database()

        db.cursor.execute(
            "DELETE FROM discord_destinations WHERE id_filmweb = (SELECT id_filmweb FROM users WHERE id_discord = %s)",
            (id_discord,),
        )

        db.connection.commit()
        db.connection.close()

        self.delete_user_from_db(id_discord)

        return True

    def add_user_to_guild(self, id_discord: int, guild_id: int):
        if self.check_user_is_in_db(id_discord) is None:
            return "User not found in database"

        id_discord = int(id_discord)
        guild_id = int(guild_id)

        db = Database()

        db.cursor.execute(
            f"SELECT * FROM discord_destinations WHERE id_filmweb = (SELECT id_filmweb FROM users WHERE id_discord = %s) AND guild_id = %s",
            (id_discord, guild_id),
        )

        result = db.cursor.fetchone()

        if result is None:
            db.cursor.execute(
                f"INSERT INTO discord_destinations (id_filmweb, guild_id) VALUES ((SELECT id_filmweb FROM users WHERE id_discord = %s), %s)",
                (id_discord, guild_id),
            )
            db.connection.commit()

        db.connection.close()

        return True

    def configure_guild(self, guild_id: int, channel_id: int):
        db = Database()

        db.cursor.execute(
            f"SELECT * FROM discord_guilds WHERE guild_id = %s",
            (guild_id,),
        )

        result = db.cursor.fetchone()

        if result is None:
            db.cursor.execute(
                f"INSERT INTO discord_guilds (guild_id, channel_id) VALUES (%s, %s)",
                (guild_id, channel_id),
            )
        else:
            db.cursor.execute(
                f"UPDATE discord_guilds SET channel_id = %s WHERE guild_id = %s",
                (channel_id, guild_id),
            )

        db.connection.commit()
        db.connection.close()

        return True
