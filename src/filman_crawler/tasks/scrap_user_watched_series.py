import datetime
import logging

import ujson

from filman_server.database.schemas import FilmWebUserWatchedMovieCreate

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
        pass
