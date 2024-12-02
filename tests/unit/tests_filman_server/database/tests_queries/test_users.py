# hell yes 1k line test

import datetime
import logging

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import filman_server.database.crud as crud
import filman_server.database.models as models


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create users
    user1 = models.User(id=1, discord_id=123456789)
    user2 = models.User(id=2, discord_id=987654321)
    user3 = models.User(id=3, discord_id=777777777)
    user4 = models.User(id=4, discord_id=888888888)
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.add(user4)
    session.commit()

    # Create filmweb movies
    filmweb_movie1 = models.FilmWebMovie(
        id=628,
        title="Matrix",
        year=1999,
        poster_url="https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp",
        community_rate=7.7,
    )
    session.add(filmweb_movie1)
    session.commit()

    # Create filmweb series
    filmweb_series1 = models.FilmWebSeries(
        id=430668,
        title="Breaking Bad",
        year=2008,
        other_year=2013,
        poster_url="https://fwcdn.pl/fpo/06/68/430668/7730445_2.10.webp",
        community_rate=8.8,
    )
    session.add(filmweb_series1)
    session.commit()

    # Create filmweb mappings
    filmweb_mapping1 = models.FilmWebUserMapping(id=1, user_id=user2.id, filmweb_id="filmweb123")
    filmweb_mapping2 = models.FilmWebUserMapping(id=2, user_id=user3.id, filmweb_id="kanye_west")
    session.add(filmweb_mapping1)
    session.add(filmweb_mapping2)
    session.commit()

    # Create discord guilds
    discord_guild1 = models.DiscordGuilds(discord_guild_id=123456789, discord_channel_id=100000)
    discord_guild2 = models.DiscordGuilds(discord_guild_id=987654321, discord_channel_id=200000)
    discord_guild3 = models.DiscordGuilds(discord_guild_id=111111111, discord_channel_id=300000)
    discord_guild4 = models.DiscordGuilds(discord_guild_id=222222222, discord_channel_id=400000)
    discord_guild5 = models.DiscordGuilds(discord_guild_id=333333333, discord_channel_id=500000)
    session.add(discord_guild1)
    session.add(discord_guild2)
    session.add(discord_guild3)
    session.add(discord_guild4)
    session.add(discord_guild5)
    session.commit()

    # Create discord destinations
    # User 1 should be in 1 guild
    destination1 = models.DiscordDestinations(user_id=user1.id, discord_guild_id=123456789)
    session.add(destination1)
    session.commit()

    # User 2 should be in 2 guilds
    destination2 = models.DiscordDestinations(user_id=user2.id, discord_guild_id=987654321)
    destination3 = models.DiscordDestinations(user_id=user2.id, discord_guild_id=111111111)
    session.add(destination2)
    session.add(destination3)
    session.commit()

    # User 3 should be in 3 guilds
    destination4 = models.DiscordDestinations(user_id=user3.id, discord_guild_id=123456789)
    destination5 = models.DiscordDestinations(user_id=user3.id, discord_guild_id=987654321)
    destination6 = models.DiscordDestinations(user_id=user3.id, discord_guild_id=111111111)
    session.add(destination4)
    session.add(destination5)
    session.add(destination6)
    session.commit()

    # User 4 should be in 4 guilds
    destination7 = models.DiscordDestinations(user_id=user4.id, discord_guild_id=123456789)
    destination8 = models.DiscordDestinations(user_id=user4.id, discord_guild_id=987654321)
    destination9 = models.DiscordDestinations(user_id=user4.id, discord_guild_id=111111111)
    destination10 = models.DiscordDestinations(user_id=user4.id, discord_guild_id=222222222)
    session.add(destination7)
    session.add(destination8)
    session.add(destination9)
    session.add(destination10)
    session.commit()

    yield session

    session.close()
    models.Base.metadata.drop_all(engine)


#
# USERS
#


def test_get_user_by_id(test_db):
    result = crud.get_user(test_db, id=1, filmweb_id=None, discord_id=None)
    assert result.id == 1
    assert result.discord_id == 123456789


def test_get_user_by_filmweb_id(test_db):
    result = crud.get_user(test_db, id=None, filmweb_id="filmweb123", discord_id=None)
    assert result.id == 2
    assert result.discord_id == 987654321


def test_get_user_by_discord_id(test_db):
    result = crud.get_user(test_db, id=None, filmweb_id=None, discord_id=123456789)
    assert result.id == 1
    assert result.discord_id == 123456789


def test_get_user_no_parameters(test_db):
    result = crud.get_user(test_db, id=None, filmweb_id=None, discord_id=None)
    assert result is None


def test_get_user_by_non_existent_id(test_db):
    result = crud.get_user(test_db, id=999, filmweb_id=None, discord_id=None)
    assert result is None


def test_get_user_by_non_existent_filmweb_id(test_db):
    result = crud.get_user(test_db, id=None, filmweb_id="nonexistent", discord_id=None)
    assert result is None


def test_get_user_by_non_existent_discord_id(test_db):
    result = crud.get_user(test_db, id=None, filmweb_id=None, discord_id=999999999)
    assert result is None


def test_get_user_empty_database():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    result = crud.get_user(session, id=1, filmweb_id=None, discord_id=None)
    assert result is None

    session.close()
    models.Base.metadata.drop_all(engine)
