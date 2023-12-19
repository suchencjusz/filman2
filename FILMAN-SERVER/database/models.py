from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    VARCHAR,
    SmallInteger,
    DateTime,
    Float,
    BIGINT,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filmweb_id = Column(String(128), index=True, unique=True)
    discord_id = Column(BIGINT, index=True, unique=True)

    filmweb_watched_movies = relationship(
        "FilmWebUserWatchedMovie", backref="user", cascade="all, delete-orphan"
    )


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    discord_color = Column(VARCHAR(length=6))


#
# DISCORD
#


class DiscordGuilds(Base):
    __tablename__ = "discord_guilds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    discord_guild_id = Column(BIGINT, index=True, unique=True)
    discord_channel_id = Column(BIGINT, index=True, unique=True)


class DiscordDestinations(Base):
    __tablename__ = "discord_destinations"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    discord_guild_id = Column(BIGINT, ForeignKey("discord_guilds.discord_guild_id"))

    user = relationship("User", backref="discord_destinations")


#
# FILMWEB
#


class __FilmwebMedia(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    year = Column(SmallInteger)
    poster_url = Column(String(128))
    community_rate = Column(Float)


class FilmWebMovie(__FilmwebMedia):
    __tablename__ = "filmweb_movies"


class FilmWebSeries(__FilmwebMedia):
    __tablename__ = "filmweb_series"


class __FilmwebWatched(Base):
    __abstract__ = True

    date = Column(DateTime)
    rate = Column(SmallInteger)
    comment = Column(String(256))
    favorite = Column(Boolean)


class FilmWebUserWatchedMovie(__FilmwebWatched):
    __tablename__ = "filmweb_user_watched_movies"

    id_media = Column(
        Integer, ForeignKey("filmweb_movies.id"), primary_key=True, index=True
    )
    id_filmweb = Column(
        String(128), ForeignKey("users.filmweb_id"), primary_key=True, index=True
    )

    movie = relationship("FilmWebMovie", backref="filmweb_user_watched_movies")


class FilmWebUserWatchedSeries(__FilmwebWatched):
    __tablename__ = "filmweb_user_watched_series"

    id_media = Column(
        Integer, ForeignKey("filmweb_series.id"), primary_key=True, index=True
    )
    id_filmweb = Column(
        String(128), ForeignKey("users.filmweb_id"), primary_key=True, index=True
    )

    series = relationship("FilmWebSeries", backref="filmweb_user_watched_series")
