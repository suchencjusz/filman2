import datetime
import logging

import ujson

from filman_server.database.schemas import FilmWebUserWatchedSeriesCreate

from .utils import (
    DiscordNotifications,
    FilmWeb,
    Task,
    Tasks,
    TaskStatus,
    TaskTypes,
    Updaters,
)


class Scraper:
    def __init__(self, headers=None, endpoint_url=None):
        self.headers = headers
        self.endpoint_url = endpoint_url
        self.fetch = Updaters(headers, endpoint_url).fetch

    def scrap(self, task: Task):
        logging.info(f"Scraping user watched movies for user: {task.task_job}")

        tasks = Tasks(self.headers, self.endpoint_url)

        last_100_watched = (
            f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/serial"
        )
        user_already_watched = f"{self.endpoint_url}/filmweb/user/watched/series/get_all?filmweb_id={task.task_job}"

        try:
            logging.debug(
                f"Fetching user already watched series from: {user_already_watched}"
            )
            user_already_watched_data = self.fetch(
                user_already_watched, params={"filmweb_id": task.task_job}
            )
            user_already_watched_data = ujson.loads(user_already_watched_data)

            if user_already_watched is not None or user_already_watched_data != []:
                user_already_watched_ids = [
                    series["series"]["id"] for series in user_already_watched_data
                ]
            else:
                user_already_watched_ids = []

        except Exception as e:
            logging.error(f"Error fetching user already watched movies: {e}")
            return "Error fetching user already watched movies"

        try:
            logging.debug(
                f"Fetching last 100 watched series from (filmweb): {last_100_watched}"
            )
            last_100_watched_data = self.fetch(last_100_watched)
            last_100_watched_data = ujson.loads(last_100_watched_data)

            if last_100_watched_data is None:
                logging.error(f"Error fetching last 100 watched for {task.task_job}")
                return "Private profile or no series watched"

        except Exception as e:
            logging.error(f"Error fetching last 100 watched series from filmweb: {e}")
            return "Error fetching last 100 watched series from filmweb"

        first_time_scrap = True if user_already_watched_ids == [] else False

        user_already_watched_ids = set(user_already_watched_ids or [])

        new_series_watched = [
            series
            for series in last_100_watched_data
            if series[0] not in user_already_watched_ids
        ]
        new_series_watched_parsed = []

        logging.debug(f"Found {len(new_series_watched)} new series watched")

        for series in new_series_watched:
            try:
                logging.debug(
                    f"Fetching user series rate for series from filmweb: {series[0]}"
                )
                series_rate_data = self.fetch(
                    f"https://www.filmweb.pl/api/v1/user/{task.task_job}/vote/serial/{series[0]}"
                )

                if series_rate_data is None:
                    logging.error(f"Error fetching series rate for series: {series[0]}")
                    continue

                series_rate_data = ujson.loads(series_rate_data)

                watched_series_info = FilmWebUserWatchedSeriesCreate(
                    id_media=series[0],
                    filmweb_id=task.task_job,
                    date=datetime.datetime.fromtimestamp(
                        series_rate_data["timestamp"] / 1000
                    ),
                    rate=series_rate_data.get("rate", 0),
                    comment=series_rate_data.get("comment", None),
                    favorite=bool(series_rate_data.get("favorite", False)),
                )

                new_series_watched_parsed.append(watched_series_info)
            except Exception as e:
                logging.error(f"Error parsing movie data: {e}")
                continue

        logging.info(f"Found {len(new_series_watched_parsed)} new series watched")

        if len(new_series_watched_parsed) == 0:
            tasks.update_task_status(task.task_id, TaskStatus.COMPLETED)
            return "No new series watched"

        logging.debug("Preparing to update data")

        try:
            update = self.update_data(
                filmweb_id=task.task_job,
                series_watched=new_series_watched_parsed,
                first_time_scrap=first_time_scrap,
                task_id=task.task_id,
            )

            if update is False:
                logging.error(f"Error updating series data for user: {task.task_job}")
                return "Error updating series data"

            logging.info(f"Updated series data for user: {task.task_job}")
            return "Data updated"
        except Exception as e:
            logging.error(f"Error updating series data for user: {task.task_job}")
            logging.error(e)

    def update_data(
        self,
        filmweb_id: str,
        series_watched: list[FilmWebUserWatchedSeriesCreate],
        first_time_scrap: bool,
        task_id: int,
    ):
        logging.debug(f"Updating series data for user: {filmweb_id}")

        filmweb = FilmWeb(self.headers, self.endpoint_url)
        tasks = Tasks(self.headers, self.endpoint_url)
        dc_notifications = DiscordNotifications(self.headers, self.endpoint_url)

        for series in series_watched:

            try:
                if filmweb.add_watched_series(series):
                    if first_time_scrap is False:
                        if (
                            dc_notifications.send_notification(
                                filmweb_id=filmweb_id,
                                media_type="series",
                                media_id=series.id_media,
                            )
                            is True
                        ):
                            logging.info(
                                f"Notification sent for series: {series.id_media}"
                            )
                        else:
                            logging.error(
                                f"Error sending notification for series: {series.id_media}"
                            )
                            continue
                else:
                    logging.error(f"Error adding watched series: {series.id_media}")
                    continue

                tasks.create_task(
                    Task(
                        task_id=0,
                        task_status=TaskStatus.QUEUED,
                        task_type=TaskTypes.SCRAP_FILMWEB_SERIES,
                        task_job=str(series.id_media),
                        task_created=datetime.datetime.now(),
                    )
                )

            except Exception as e:
                logging.error(f"Error updating series data for user: {filmweb_id}")
                logging.error(e)
                continue

        tasks.update_task_status(task_id, TaskStatus.COMPLETED)

        return True
