from sqlalchemy.orm import Session
import sqlalchemy.exc

from . import models, schemas

#
# USERS
#


def get_user(
    db: Session, id: int | None, filmweb_id: str | None, discord_id: int | None
):
    if id:
        return db.query(models.User).filter(models.User.id == id).first()
    elif filmweb_id:
        return (
            db.query(models.User).filter(models.User.filmweb_id == filmweb_id).first()
        )
    elif discord_id:
        return (
            db.query(models.User).filter(models.User.discord_id == discord_id).first()
        )
    else:
        return None


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_destinations(db: Session, user_id: int):
    return db.query(models.DiscordDestinations).filter_by(user_id=user_id).all()


def get_user_destination(db: Session, user_id: int, discord_guild_id: int):
    return (
        db.query(models.DiscordDestinations)
        .filter_by(user_id=user_id, discord_guild_id=discord_guild_id)
        .first()
    )


def set_user_destination(db: Session, user_id: int, discord_guild_id: int):
    db_dest = (
        db.query(models.DiscordDestinations)
        .filter_by(user_id=user_id, discord_guild_id=discord_guild_id)
        .first()
    )

    if db_dest is None:
        db_dest = models.DiscordDestinations(
            user_id=user_id, discord_guild_id=discord_guild_id
        )
        db.add(db_dest)
    else:
        db_dest.discord_guild_id = discord_guild_id

    db.commit()
    db.refresh(db_dest)

    return db_dest


def delete_user_destination(db: Session, user_id: int, discord_guild_id: int):
    db_dest = (
        db.query(models.DiscordDestinations)
        .filter_by(user_id=user_id, discord_guild_id=discord_guild_id)
        .first()
    )

    if db_dest is None:
        raise Exception("User not in guild")

    db.delete(db_dest)
    db.commit()

    return db_dest


def delete_user_destitations(db: Session, user_id: int):
    destinations = db.query(models.DiscordDestinations).filter(
        models.DiscordDestinations.user_id == user_id
    )

    destinations.delete()

    db.commit()


#
# DISCORD
#


def get_guild(db: Session, discord_guild_id: int):
    return (
        db.query(models.DiscordGuilds)
        .filter(models.DiscordGuilds.discord_guild_id == discord_guild_id)
        .first()
    )


def set_guild(db: Session, guild: schemas.DiscordGuildsCreate):
    db_guild = get_guild(db, guild.discord_guild_id)
    if db_guild is None:
        return create_guild(db, guild)
    db_guild.discord_channel_id = guild.discord_channel_id
    db.commit()
    db.refresh(db_guild)
    return db_guild


def create_guild(db: Session, guild: schemas.DiscordGuildsCreate):
    db_guild = models.DiscordGuilds(**guild.model_dump())
    db.add(db_guild)
    db.commit()
    db.refresh(db_guild)
    return db_guild


#
# FILMWEB MOVIES
#


def get_movie_filmweb_id(db: Session, id: int):
    return db.query(models.FilmWebMovie).filter(models.FilmWebMovie.id == id).first()


def create_filmweb_movie(db: Session, movie: schemas.FilmWebMovie):
    db_movie = models.FilmWebMovie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_filmweb_movie(db: Session, movie: schemas.FilmWebMovie):
    db_movie = get_movie_filmweb_id(db, movie.id)
    if db_movie is None:
        return create_filmweb_movie(db, movie)
    db_movie.title = movie.title
    db_movie.year = movie.year
    db_movie.poster_url = movie.poster_url
    db_movie.community_rate = movie.community_rate
    db.commit()
    db.refresh(db_movie)
    return db_movie


#
# FILMWEB WATCHED
#

# MOVIES


def create_filmweb_user_watched_movie(
    db: Session, user_watched_movie: schemas.FilmWebUserWatchedMovieCreate
):
    watched_movie = get_movie_filmweb_id(db, user_watched_movie.id_media)

    if watched_movie is None:
        watched_movie = schemas.FilmWebMovieCreate(
            id=user_watched_movie.id_media,
            title=None,
            year=None,
            poster_url=None,
            community_rate=None,
        )

        create_filmweb_movie(db, watched_movie)

    db_movie_watched = (
        db.query(models.FilmWebUserWatchedMovie)
        .filter(
            models.FilmWebUserWatchedMovie.id_filmweb == user_watched_movie.id_filmweb,
            models.FilmWebUserWatchedMovie.id_media == user_watched_movie.id_media,
        )
        .first()
    )

    if db_movie_watched is not None:
        return sqlalchemy.exc.IntegrityError(
            "Movie already in user watched", None, None
        )

    db_movie = models.FilmWebUserWatchedMovie(**user_watched_movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def get_filmweb_user_watched_movies(db: Session, id_filmweb: str):
    return (
        db.query(models.FilmWebUserWatchedMovie)
        .filter(models.FilmWebUserWatchedMovie.id_filmweb == id_filmweb)
        .all()
    )


def get_filmweb_user_watched_movies_ids(db: Session, id_filmweb: str):
    result = (
        db.query(models.FilmWebUserWatchedMovie.id_media)  # select only the id field
        .filter(models.FilmWebUserWatchedMovie.id_filmweb == id_filmweb)
        .all()
    )
    return [id_media for (id_media,) in result]  # extract ids from tuples
