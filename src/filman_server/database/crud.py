import logging
import os
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas

#
# USERS
#

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_user(
    db: Session,
    id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
) -> models.User | None:
    if id:
        return db.query(models.User).filter(models.User.id == id).first()
    elif filmweb_id:
        return (
            db.query(models.User)
            .join(models.FilmWebUserMapping)
            .filter(models.FilmWebUserMapping.filmweb_id == filmweb_id)
            .first()
        )
    elif discord_id:
        return db.query(models.User).filter(models.User.discord_id == discord_id).first()
    else:
        return None


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(
    db: Session,
    user: schemas.UserCreate,
) -> models.User:
    db_user = models.User(discord_id=user.discord_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_destinations(
    db: Session,
    user_id: int | None,
    discord_user_id: int | None,
) -> list[models.DiscordDestinations] | None:
    user = get_user(db, user_id, None, discord_user_id)

    if user is None:
        return None

    return db.query(models.DiscordDestinations).filter_by(user_id=user.id).all()


def get_user_destinations_channels(
    db: Session,
    user_id: int | None,
    discord_user_id: int | None,
) -> list[int]:
    query = db.query(models.DiscordGuilds.discord_channel_id).join(
        models.DiscordDestinations,
        models.DiscordDestinations.discord_guild_id == models.DiscordGuilds.discord_guild_id,
    )
    if user_id:
        query = query.filter(models.DiscordDestinations.user_id == user_id)
    if discord_user_id:
        query = query.filter(models.DiscordDestinations.discord_user_id == discord_user_id)
    return [channel_id for (channel_id,) in query.all()]


# It is used to check if user is in discord guild only for that!
def get_user_destination(
    db: Session,
    user_id: int | None,
    discord_user_id: int | None,
    discord_guild_id: int,
) -> models.DiscordDestinations | None:
    user = get_user(db, user_id, None, discord_user_id)

    if user is None:
        return None

    return db.query(models.DiscordDestinations).filter_by(user_id=user.id, discord_guild_id=discord_guild_id).first()


def set_user_destination(
    db: Session,
    user_id: int,
    discord_guild_id: int,
) -> models.DiscordDestinations:
    db_dest = db.query(models.DiscordDestinations).filter_by(user_id=user_id, discord_guild_id=discord_guild_id).first()

    if db_dest is None:
        db_dest = models.DiscordDestinations(user_id=user_id, discord_guild_id=discord_guild_id)
        db.add(db_dest)
    else:
        db_dest.discord_guild_id = discord_guild_id

    db.commit()
    db.refresh(db_dest)

    return db_dest


def delete_user_destination(
    db: Session,
    user_id: int | None,
    discord_user_id: int | None,
    discord_guild_id: int,
) -> models.DiscordDestinations | None:
    user = get_user(db, user_id, None, discord_user_id)

    if user is None:
        return None

    db_dest = db.query(models.DiscordDestinations).filter_by(user_id=user.id, discord_guild_id=discord_guild_id).first()

    if db_dest is None:
        return None

    db.delete(db_dest)
    db.commit()

    return db_dest


def delete_user_destinations(
    db: Session,
    user_id: int | None,
    discord_user_id: int | None,
) -> models.DiscordDestinations | None:
    for dest in get_user_destinations(db, user_id, discord_user_id):
        delete_user_destination(db, user_id, discord_user_id, dest.discord_guild_id)

    return None

    # destinations = db.query(models.DiscordDestinations).filter(models.DiscordDestinations.user_id == user_id)
    # destinations.delete()
    # db.commit()


#
# DISCORD
#


def get_guild(db: Session, discord_guild_id: int):
    return db.query(models.DiscordGuilds).filter(models.DiscordGuilds.discord_guild_id == discord_guild_id).first()


def get_guild_members(db: Session, discord_guild_id: int) -> list[schemas.User]:
    return (
        db.query(models.User)
        .join(models.DiscordDestinations)
        .filter(models.DiscordDestinations.discord_guild_id == discord_guild_id)
        .all()
    )


# set = create
def set_guild(db: Session, guild: schemas.DiscordGuildsCreate):
    db_guild = get_guild(db, guild.discord_guild_id)
    if db_guild is None:
        return create_guild(db, guild)
    db_guild.discord_channel_id = guild.discord_channel_id
    db.commit()
    db.refresh(db_guild)
    return db_guild


def create_guild(db: Session, guild: schemas.DiscordGuildsCreate):
    # db_guild = models.DiscordGuilds(**guild.model_dump())
    db_guild = models.DiscordGuilds(
        discord_guild_id=guild.discord_guild_id,
        discord_channel_id=guild.discord_channel_id,
    )

    db.add(db_guild)
    db.commit()
    db.refresh(db_guild)
    return db_guild


# should by called when bot leaves discord server
# also should remove connected destinations
def delete_guild(db: Session, discord_guild_id: int):
    db_guild = get_guild(db, discord_guild_id)
    if db_guild is None:
        return None

    # delete all connected destinations
    db.query(models.DiscordDestinations).filter(
        models.DiscordDestinations.discord_guild_id == discord_guild_id
    ).delete()

    db.delete(db_guild)
    db.commit()

    return db_guild


def get_guilds(db: Session):
    return db.query(models.DiscordGuilds).all()


#
# FILMWEB MOVIES
#


def get_movie_filmweb_id(db: Session, id: int) -> models.FilmWebMovie | None:
    return db.query(models.FilmWebMovie).filter(models.FilmWebMovie.id == id).first()


def create_filmweb_movie(db: Session, movie: schemas.FilmWebMovie) -> models.FilmWebMovie:
    existing_movie = db.query(models.FilmWebMovie).filter_by(id=movie.id).first()
    if existing_movie:
        return existing_movie

    db_movie = models.FilmWebMovie(
        id=movie.id,
        title=movie.title,
        year=movie.year,
        poster_url=movie.poster_url,
        community_rate=movie.community_rate,
        critics_rate=movie.critics_rate,
    )

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return db_movie


def update_filmweb_movie(db: Session, movie: schemas.FilmWebMovie):
    db_movie = get_movie_filmweb_id(db, movie.id)

    if db_movie is None:
        return create_filmweb_movie(db, movie)

    logging.debug(f"Updating movie: {movie.title}")
    logging.debug(f"movie data before")
    logging.debug(f"{db_movie.title}")
    logging.debug(f"{db_movie.year}")
    logging.debug(f"{db_movie.poster_url}")
    logging.debug(f"{db_movie.community_rate}")
    logging.debug(f"{db_movie.critics_rate}")
    logging.debug(f"movie data after")

    db_movie.title = movie.title
    db_movie.year = movie.year
    db_movie.poster_url = movie.poster_url
    db_movie.community_rate = movie.community_rate
    db_movie.critics_rate = movie.critics_rate

    logging.debug(f"{db_movie.title}")
    logging.debug(f"{db_movie.year}")
    logging.debug(f"{db_movie.poster_url}")
    logging.debug(f"{db_movie.community_rate}")
    logging.debug(f"{db_movie.critics_rate}")

    db.commit()
    db.refresh(db_movie)

    return db_movie


#
# FILMWEB SERIES
#


def get_series_filmweb_id(db: Session, id: int):
    return db.query(models.FilmWebSeries).filter(models.FilmWebSeries.id == id).first()


def create_filmweb_series(db: Session, series: schemas.FilmWebSeries):
    existing_series = db.query(models.FilmWebSeries).filter_by(id=series.id).first()
    if existing_series:
        return existing_series

    db_series = models.FilmWebSeries(
        id=series.id,
        title=series.title,
        year=series.year,
        other_year=series.other_year,
        poster_url=series.poster_url,
        community_rate=series.community_rate,
        critics_rate=series.critics_rate,
    )

    db.add(db_series)
    db.commit()
    db.refresh(db_series)

    return db_series


def update_filmweb_series(db: Session, series: schemas.FilmWebSeries):
    db_series = get_series_filmweb_id(db, series.id)

    if db_series is None:
        return create_filmweb_series(db, series)

    db_series.title = series.title
    db_series.year = series.year
    db_series.poster_url = series.poster_url
    db_series.community_rate = series.community_rate
    db_series.other_year = series.other_year
    db_series.critics_rate = series.critics_rate

    db.commit()
    db.refresh(db_series)

    return db_series


#
# FILMWEB WATCHED
#

# FILMWEB USER MAPPING


def get_filmweb_user_mapping(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
) -> models.FilmWebUserMapping | None:
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        return None

    return db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()


# sets filmweb user nickname to corelate with discord user (main user in db)
def set_filmweb_user_mapping(
    db: Session, mapping: schemas.FilmWebUserMappingCreate
) -> models.FilmWebUserMapping | None:
    user = get_user(db, mapping.user_id, None, None)

    if user is None:
        return None

    db_mapping = db.query(models.FilmWebUserMapping).filter_by(user_id=user.id).first()

    # creates
    if db_mapping is None:
        db_mapping = models.FilmWebUserMapping(user_id=user.id, filmweb_id=mapping.filmweb_id)
        db.add(db_mapping)
    # updates
    else:
        db_mapping.filmweb_id = mapping.filmweb_id

    db.commit()
    db.refresh(db_mapping)

    return db_mapping


def delete_filmweb_user_mapping(
    db: Session,
    user_id: int | None,
    discord_id: int | None,
    filmweb_id: str | None,
) -> bool | None:
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        logging.debug(f"User not found for user_id {user_id} and filmweb_id {filmweb_id}")
        return False

    db_mapping = db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()

    if db_mapping is None:
        logging.debug(f"Mapping not found for user {user.id} and filmweb_id {filmweb_id}")
        return None

    db.delete(db_mapping)
    db.commit()

    return True


# MOVIES WATCHED


def create_filmweb_user_watched_movie(db: Session, user_watched_movie: schemas.FilmWebUserWatchedMovieCreate):
    watched_movie = get_movie_filmweb_id(db, user_watched_movie.id_media)

    if watched_movie is None:
        watched_movie = schemas.FilmWebMovieCreate(
            id=user_watched_movie.id_media,
        )

        create_filmweb_movie(db, watched_movie)

    db_movie_watched = (
        db.query(models.FilmWebUserWatchedMovie)
        .filter(
            models.FilmWebUserWatchedMovie.filmweb_id == user_watched_movie.filmweb_id,
            models.FilmWebUserWatchedMovie.id_media == user_watched_movie.id_media,
        )
        .first()
    )

    if db_movie_watched is not None:
        raise IntegrityError("Movie already in user watched", None, None)

    db_movie = models.FilmWebUserWatchedMovie(
        id_media=user_watched_movie.id_media,
        filmweb_id=user_watched_movie.filmweb_id,
        date=user_watched_movie.date,
        rate=user_watched_movie.rate,
        comment=user_watched_movie.comment,
        favorite=user_watched_movie.favorite,
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def get_filmweb_user_watched_movie(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
    id_media: int,
):
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        return None

    # Get the filmweb_id from the mapping if not provided
    if filmweb_id is None:
        filmweb_mapping = (
            db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()
        )
        if filmweb_mapping is None:
            return None
        filmweb_id = filmweb_mapping.filmweb_id

    return (
        db.query(models.FilmWebUserWatchedMovie)
        .filter(
            models.FilmWebUserWatchedMovie.filmweb_id == filmweb_id,
            models.FilmWebUserWatchedMovie.id_media == id_media,
        )
        .first()
    )


def get_filmweb_user_watched_movies(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
):
    # Fetch the user based on user_id, filmweb_id, or discord_id
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        return None

    # If filmweb_id is not provided, get it from the user mapping
    if filmweb_id is None:
        filmweb_mapping = (
            db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()
        )
        if filmweb_mapping is None:
            return None
        filmweb_id = filmweb_mapping.filmweb_id

    # Query the database for all watched movies for the given filmweb_id
    watched_movies = (
        db.query(models.FilmWebUserWatchedMovie).filter(models.FilmWebUserWatchedMovie.filmweb_id == filmweb_id).all()
    )

    return watched_movies


def delete_filmweb_user_watched_movies(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
) -> bool:
    user_mapping = get_filmweb_user_mapping(db, user_id, filmweb_id, discord_id)

    if user_mapping is None:
        return False

    filmweb_id = user_mapping.filmweb_id

    db.query(models.FilmWebUserWatchedMovie).filter(models.FilmWebUserWatchedMovie.filmweb_id == filmweb_id).delete()
    db.commit()

    return True


def get_filmweb_watched_movies_all(db: Session) -> list[models.FilmWebUserWatchedMovie]:
    return db.query(models.FilmWebUserWatchedMovie).all()


# SERIES WATCHED
def create_filmweb_user_watched_series(db: Session, user_watched_series: schemas.FilmWebUserWatchedSeriesCreate):
    watched_series = get_series_filmweb_id(db, user_watched_series.id_media)

    if watched_series is None:
        watched_series = schemas.FilmWebSeriesCreate(
            id=user_watched_series.id_media,
        )

        create_filmweb_series(db, watched_series)

    db_series_watched = (
        db.query(models.FilmWebUserWatchedSeries)
        .filter(
            models.FilmWebUserWatchedSeries.filmweb_id == user_watched_series.filmweb_id,
            models.FilmWebUserWatchedSeries.id_media == user_watched_series.id_media,
        )
        .first()
    )

    if db_series_watched is not None:
        raise IntegrityError("Series already in user watched", None, None)

    db_series = models.FilmWebUserWatchedSeries(
        id_media=user_watched_series.id_media,
        filmweb_id=user_watched_series.filmweb_id,
        date=user_watched_series.date,
        rate=user_watched_series.rate,
        comment=user_watched_series.comment,
        favorite=user_watched_series.favorite,
    )
    db.add(db_series)
    db.commit()
    db.refresh(db_series)
    return db_series


def get_filmweb_user_watched_series_all(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
):
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        return None

    # Get the filmweb_id from the mapping if not provided
    if filmweb_id is None:
        filmweb_mapping = (
            db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()
        )
        if filmweb_mapping is None:
            return None
        filmweb_id = filmweb_mapping.filmweb_id

    return (
        db.query(models.FilmWebUserWatchedSeries).filter(models.FilmWebUserWatchedSeries.filmweb_id == filmweb_id).all()
    )


def get_filmweb_user_watched_series(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
    id_media: int,
):
    user = get_user(db, user_id, filmweb_id, discord_id)

    if user is None:
        return None

    # Get the filmweb_id from the mapping if not provided
    if filmweb_id is None:
        filmweb_mapping = (
            db.query(models.FilmWebUserMapping).filter(models.FilmWebUserMapping.user_id == user.id).first()
        )
        if filmweb_mapping is None:
            return None
        filmweb_id = filmweb_mapping.filmweb_id

    return (
        db.query(models.FilmWebUserWatchedSeries)
        .filter(
            models.FilmWebUserWatchedSeries.filmweb_id == filmweb_id,
            models.FilmWebUserWatchedSeries.id_media == id_media,
        )
        .first()
    )


def delete_filmweb_user_watched_series(
    db: Session,
    user_id: int | None,
    filmweb_id: str | None,
    discord_id: int | None,
) -> bool:
    user_mapping = get_filmweb_user_mapping(db, user_id, filmweb_id, discord_id)

    if user_mapping is None:
        return False

    filmweb_id = user_mapping.filmweb_id

    db.query(models.FilmWebUserWatchedSeries).filter(models.FilmWebUserWatchedSeries.filmweb_id == filmweb_id).delete()
    db.commit()

    return True


def get_filmweb_watched_series_all(
    db: Session,
) -> list[models.FilmWebUserWatchedSeries]:
    return db.query(models.FilmWebUserWatchedSeries).all()


#
# TASKS
#


def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())

    db_task.task_created = datetime.now()

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def __change_task_status(db: Session, task_id: int, task_status: schemas.TaskStatus):
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if db_task is None:
        return None

    db_task.task_status = task_status

    task_started = datetime.now() if task_status == schemas.TaskStatus.RUNNING else None
    if task_started is not None:
        db_task.task_started = task_started

    task_finished = datetime.now() if task_status == schemas.TaskStatus.COMPLETED else None
    if task_finished is not None:
        db_task.task_finished = task_finished

    # logging.debug(f"t: {db_task.task_job}")
    # logging.debug(f"t: {db_task.task_type}")
    # logging.debug(f"t: {db_task.task_status}")
    # logging.debug(f"t: {db_task.task_created}")
    # logging.debug(f"t: {db_task.task_started}")
    # logging.debug(f"t: {db_task.task_finished}")

    db.commit()
    db.refresh(db_task)
    return db_task


def update_task_status(db: Session, task_id: int, task_status: schemas.TaskStatus):
    return __change_task_status(db, task_id, task_status)


def get_task_to_do(db: Session, task_types: schemas.TaskTypes, head: bool = False):
    task_to_do = (
        db.query(models.Task)
        .filter(
            models.Task.task_status == schemas.TaskStatus.QUEUED,
            models.Task.task_type.in_(task_types),
        )
        .first()
    )

    if task_to_do is None:
        return None

    if head:
        return task_to_do
    else:
        return __change_task_status(db, task_to_do.task_id, schemas.TaskStatus.RUNNING)


def remove_completed_tasks(db: Session):
    db.query(models.Task).filter(models.Task.task_status == schemas.TaskStatus.COMPLETED).delete()
    db.commit()


#
# MULTIPLE TASKS GENERATION
#

# MOVIES


def create_scrap_filmweb_users_movies_task(db: Session) -> bool:
    filmweb_users = db.query(models.FilmWebUserMapping).all()

    for user in filmweb_users:
        create_task(
            db,
            schemas.TaskCreate(
                task_status=schemas.TaskStatus.QUEUED,
                task_type=schemas.TaskTypes.SCRAP_FILMWEB_USER_WATCHED_MOVIES,
                task_job=str(user.filmweb_id),
            ),
        )

    return True


def create_scrap_filmweb_movies_task(db: Session) -> bool:
    filmweb_movies = db.query(models.FilmWebMovie).all()

    for movie in filmweb_movies:
        create_task(
            db,
            schemas.TaskCreate(
                task_status=schemas.TaskStatus.QUEUED,
                task_type=schemas.TaskTypes.SCRAP_FILMWEB_MOVIE,
                task_job=str(movie.id),
            ),
        )

    return True


# SERIES


def create_scrap_filmweb_users_series_task(db: Session) -> bool:
    filmweb_users = db.query(models.FilmWebUserMapping).all()

    for user in filmweb_users:
        create_task(
            db,
            schemas.TaskCreate(
                task_status=schemas.TaskStatus.QUEUED,
                task_type=schemas.TaskTypes.SCRAP_FILMWEB_USER_WATCHED_SERIES,
                task_job=str(user.filmweb_id),
            ),
        )

    return True


def create_scrap_filmweb_series_task(db: Session) -> bool:
    filmweb_series = db.query(models.FilmWebSeries).all()

    for series in filmweb_series:
        create_task(
            db,
            schemas.TaskCreate(
                task_status=schemas.TaskStatus.QUEUED,
                task_type=schemas.TaskTypes.SCRAP_FILMWEB_SERIES,
                task_job=str(series.id),
            ),
        )

    return True


#
# TASKS UPDATES/MGMT
#


def update_stuck_tasks(db: Session, minutes: int = 15):  # dodaj minuty
    stuck_tasks = (
        db.query(models.Task)
        .filter(models.Task.task_status == schemas.TaskStatus.RUNNING)
        .filter(models.Task.task_started < datetime.now() - timedelta(minutes=minutes))
        .all()
    )

    for task in stuck_tasks:
        task.task_status = schemas.TaskStatus.QUEUED
        task.task_started = None
        db.commit()

    return True


def update_old_tasks(db: Session, minutes: int = 30):
    db.query(models.Task).filter(models.Task.task_created < datetime.now() - timedelta(minutes=minutes)).delete()
    db.commit()

    return True
