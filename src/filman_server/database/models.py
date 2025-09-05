from sqlalchemy import (
    BIGINT,
    VARCHAR,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    discord_id = Column(BIGINT, index=True, unique=True)

    discord_destinations = relationship("DiscordDestinations", back_populates="user", cascade="all, delete-orphan")

    filmweb_user_mapping = relationship(
        "FilmWebUserMapping",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class FilmWebUserMapping(Base):
    __tablename__ = "filmweb_user_mapping"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, unique=True)
    filmweb_id = Column(String(128), index=True, unique=True)

    user = relationship("User", back_populates="filmweb_user_mapping")
    watched_movies = relationship(
        "FilmWebUserWatchedMovie",
        back_populates="filmweb_user_mapping",
        cascade="all, delete-orphan",
    )
    watched_series = relationship(
        "FilmWebUserWatchedSeries",
        back_populates="filmweb_user_mapping",
        cascade="all, delete-orphan",
    )


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

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    discord_guild_id = Column(BIGINT, ForeignKey("discord_guilds.discord_guild_id"), primary_key=True)
    user = relationship("User", back_populates="discord_destinations")


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
    critics_rate = Column(Float)


class FilmWebMovie(__FilmwebMedia):
    __tablename__ = "filmweb_movies"


class FilmWebSeries(__FilmwebMedia):
    __tablename__ = "filmweb_series"

    other_year = Column(SmallInteger)


class __FilmwebWatched(Base):
    __abstract__ = True

    date = Column(DateTime)
    rate = Column(SmallInteger)
    comment = Column(String(1024))
    favorite = Column(Boolean)


class FilmWebUserWatchedMovie(__FilmwebWatched):
    __tablename__ = "filmweb_user_watched_movies"

    id_media = Column(Integer, ForeignKey("filmweb_movies.id"), primary_key=True, index=True)
    filmweb_id = Column(
        String(128),
        ForeignKey("filmweb_user_mapping.filmweb_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    movie = relationship("FilmWebMovie", backref="filmweb_user_watched_movies")
    filmweb_user_mapping = relationship("FilmWebUserMapping", back_populates="watched_movies")


class FilmWebUserWatchedSeries(__FilmwebWatched):
    __tablename__ = "filmweb_user_watched_series"

    id_media = Column(Integer, ForeignKey("filmweb_series.id"), primary_key=True, index=True)
    filmweb_id = Column(
        String(128),
        ForeignKey("filmweb_user_mapping.filmweb_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    series = relationship("FilmWebSeries", backref="filmweb_user_watched_series")
    filmweb_user_mapping = relationship("FilmWebUserMapping", back_populates="watched_series")


#
# TASKS
#


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_status = Column(String(32))
    task_type = Column(String(64))
    task_job = Column(String(256))
    task_created = Column(DateTime)
    task_started = Column(DateTime)
    task_finished = Column(DateTime)
