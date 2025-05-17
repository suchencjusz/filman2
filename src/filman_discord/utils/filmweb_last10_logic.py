from filman_server.database.models import FilmWebMovie, FilmWebSeries
from filman_discord.utils.star_counter import star_emoji_counter

from datetime import datetime


def last10(media: list, typ:str) -> str:
    """

    arg:
        media: list of media to be sorted
        typ: type of media (movie or series)
    
    Sorts the list of media, add stars, title and year to the list and returns the last 10 items.
    
    """

    return last_n_media(media, typ, 10)


def last_n_media(media: list, typ:str, n:int) -> str:
    """
    arg:
        media: list of media to be sorted
        typ: type of media (movie or series)
        n: number of items to return
    
    Sorts the list of media, add stars, title and year to the list and returns the last n items.
    
    """
    
    media = sorted(media, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%dT%H:%M:%S"), reverse=True)

    if len(media) == 0:
        return []

    if len(media) > n:
        media = media[0:n]

    _to_return = ""

    typ = "movie" if typ == "movies" else "series"

    for m in media:
        _to_return += f"{star_emoji_counter(m['rate'])} {m[typ]['title']} ({m[typ]['year']})\n"

    return _to_return