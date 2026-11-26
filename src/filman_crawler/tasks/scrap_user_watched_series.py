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
    extract_vote_media_ids,
    fetch_filmweb_user_id,
)


class Scraper:
    def __init__(self, headers=None, endpoint_url=None, session=None, server_session=None):
        self.headers = headers
        self.endpoint_url = endpoint_url.rstrip("/") if endpoint_url else endpoint_url
        self.session = session
        self.server_session = server_session
        self.fetch = Updaters(headers, self.endpoint_url, session=session).fetch
        self.server_fetch = Updaters(headers, self.endpoint_url, session=server_session).fetch
        self._filmweb_user_id_cache: dict[str, int] = {}

    def _resolve_filmweb_user_id(self, filmweb_id: str) -> int | None:
        if filmweb_id in self._filmweb_user_id_cache:
            return self._filmweb_user_id_cache[filmweb_id]

        filmweb_user_id = fetch_filmweb_user_id(filmweb_id, self.headers, session=self.session)
        if filmweb_user_id is None:
            return None

        self._filmweb_user_id_cache[filmweb_id] = filmweb_user_id
        return filmweb_user_id

    def scrap(self, task: Task) -> bool:
        logging.info(f"Scraping user watched series for user: {task.task_job}")

        tasks = Tasks(self.headers, self.endpoint_url, session=self.server_session)

        filmweb_user_id = self._resolve_filmweb_user_id(task.task_job)
        if filmweb_user_id is None:
            logging.error(f"Error resolving Filmweb user id for {task.task_job}")
            return False

        last_100_watched = f"https://www.filmweb.pl/api/v1/users/{filmweb_user_id}/votes/serial"
        user_already_watched = f"{self.endpoint_url}/filmweb/user/watched/series/get_all"

        try:
            logging.debug(f"Fetching user already watched series from: {user_already_watched}")
            user_already_watched_raw = self.server_fetch(user_already_watched, params={"filmweb_id": task.task_job})
            if user_already_watched_raw is None:
                logging.error(f"Error fetching user already watched series for {task.task_job}")
                return False

            user_already_watched_data = ujson.loads(user_already_watched_raw)
            if user_already_watched_data:
                user_already_watched_ids = [series["series"]["id"] for series in user_already_watched_data]
            else:
                user_already_watched_ids = []

        except Exception as e:
            logging.error(f"Error fetching user already watched series: {e}")
            return False

        try:
            logging.debug(f"Fetching last 100 watched series from (filmweb): {last_100_watched}")
            last_100_watched_raw = self.fetch(last_100_watched)
            if last_100_watched_raw is None:
                logging.error(f"Error fetching last 100 watched for {task.task_job}")
                return False

            last_100_watched_data = ujson.loads(last_100_watched_raw)
            if last_100_watched_data is None:
                logging.error(f"Error fetching last 100 watched for {task.task_job}")
                return False

            votes = []
            if isinstance(last_100_watched_data, dict):
                votes = last_100_watched_data.get("votes", [])
            elif isinstance(last_100_watched_data, list):
                votes = last_100_watched_data

        except Exception as e:
            logging.error(f"Error fetching last 100 watched series from filmweb: {e}")
            return False

        first_time_scrap = user_already_watched_ids == []
        already_watched_set = set(user_already_watched_ids)

        series_ids = extract_vote_media_ids(votes)
        new_series_watched = [series_id for series_id in series_ids if series_id not in already_watched_set]
        new_series_watched_parsed = []

        logging.debug(f"Found {len(new_series_watched)} new series watched")

        for series_id in new_series_watched:
            try:
                logging.debug(f"Fetching user series rate for series from filmweb: {series_id}")
                series_rate_data = self.fetch(
                    f"https://www.filmweb.pl/api/v1/users/{filmweb_user_id}/votes/serial/{series_id}"
                )

                if series_rate_data is None:
                    logging.error(f"Error fetching series rate for series: {series_id}")
                    continue

                series_rate_data = ujson.loads(series_rate_data)
                if not isinstance(series_rate_data, dict) or series_rate_data.get("timestamp") is None:
                    logging.error(f"Invalid series rate payload for series: {series_id}")
                    continue

                watched_series_info = FilmWebUserWatchedSeriesCreate(
                    id_media=series_id,
                    filmweb_id=task.task_job,
                    date=datetime.datetime.fromtimestamp(series_rate_data["timestamp"] / 1000),
                    rate=series_rate_data.get("rate", 0),
                    comment=series_rate_data.get("comment", None),
                    favorite=bool(series_rate_data.get("favorite", False)),
                )

                new_series_watched_parsed.append(watched_series_info)
            except Exception as e:
                logging.error(f"Error parsing series data: {e}")
                continue

        logging.info(f"Found {len(new_series_watched_parsed)} new series watched")

        if len(new_series_watched_parsed) == 0:
            return tasks.update_task_status(task.task_id, TaskStatus.COMPLETED)

        logging.debug("Preparing to update data")

        try:
            update = self.update_data(
                filmweb_id=task.task_job,
                series_watched=new_series_watched_parsed,
                first_time_scrap=first_time_scrap,
                task_id=task.task_id,
            )

            if not update:
                logging.error(f"Error updating series data for user: {task.task_job}")
                return False

            logging.info(f"Updated series data for user: {task.task_job}")
            return True
        except Exception as e:
            logging.error(f"Error updating series data for user: {task.task_job}")
            logging.error(e)
            return False

    def update_data(
        self,
        filmweb_id: str,
        series_watched: list[FilmWebUserWatchedSeriesCreate],
        first_time_scrap: bool,
        task_id: int,
    ) -> bool:
        logging.debug(f"Updating series data for user: {filmweb_id}")

        filmweb = FilmWeb(self.headers, self.endpoint_url, session=self.server_session)
        tasks = Tasks(self.headers, self.endpoint_url, session=self.server_session)
        dc_notifications = DiscordNotifications(self.headers, self.endpoint_url, session=self.server_session)

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
                            logging.info(f"Notification sent for series: {series.id_media}")
                        else:
                            logging.error(f"Error sending notification for series: {series.id_media}")
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

        return tasks.update_task_status(task_id, TaskStatus.COMPLETED)
