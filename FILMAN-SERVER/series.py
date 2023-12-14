import time

from db import Database
from tasks import TasksManager


class Series:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.year = kwargs.get("year")
        self.other_year = kwargs.get("other_year")
        self.poster_uri = kwargs.get("poster_uri")
        self.community_rate = kwargs.get("community_rate")

    def __str__(self):
        return f"{self.title} ({self.year})"


class SeriesManager:
    def __init__(self):
        pass

    def add_series_to_db(self, series):
        db = Database()

        db.cursor.execute(f"SELECT * FROM series WHERE id = %s", (series.id,))

        result = db.cursor.fetchone()

        if result is None:
            db.cursor.execute(
                f"INSERT INTO series (id, updated_unixtime, title, year, other_year, poster_uri, community_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    series.id,
                    int(time.time()),
                    series.title,
                    series.year,
                    series.other_year,
                    series.poster_uri,
                    series.community_rate,
                ),
            )

            db.connection.commit()
            db.connection.close()

            return True

        db.cursor.execute(
            f"UPDATE series SET updated_unixtime = %s, title = %s, year = %s, other_year = %s, poster_uri = %s, community_rate = %s WHERE id = %s",
            (
                int(time.time()),
                series.title,
                series.year,
                series.other_year,
                series.poster_uri,
                series.community_rate,
                series.id,
            ),
        )

        db.connection.commit()
        db.connection.close()

        return True

    def get_series_by_id(self, id):
        db = Database()
        db.cursor.execute(f"SELECT * FROM series WHERE id = {id}")

        result = db.cursor.fetchone()

        if result is None:
            task_manager = TasksManager()
            task_manager.new_task("scrap_series", id)

            return None
        else:
            return Series(
                id=result[0],
                title=result[3],
                year=result[4],
                other_year=result[5],
                poster_uri=result[6],
                community_rate=result[7],
            )
