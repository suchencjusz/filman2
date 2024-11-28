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


#
# DISCORD GUILDS
#


def test_get_guild_by_id(test_db):
    result = crud.get_guild(test_db, discord_guild_id=123456789)
    assert result.discord_guild_id == 123456789
    assert result.discord_channel_id == 100000


def test_set_guild(test_db):
    guild = models.DiscordGuilds(discord_guild_id=444444444, discord_channel_id=600000)
    result = crud.set_guild(test_db, guild)
    assert result.discord_guild_id == 444444444
    assert result.discord_channel_id == 600000

    result = crud.get_guild(test_db, discord_guild_id=444444444)
    assert result.discord_guild_id == 444444444
    assert result.discord_channel_id == 600000


def test_delete_guild(test_db):
    result = crud.delete_guild(test_db, discord_guild_id=444444444)
    assert result.discord_guild_id == 444444444

    result = crud.get_guild(test_db, discord_guild_id=444444444)
    assert result is None


def test_get_guilds(test_db):
    result = crud.get_guilds(test_db)
    assert len(result) == 5


def test_get_guild_members(test_db):
    result = crud.get_guild_members(test_db, discord_guild_id=123456789)
    assert len(result) == 3

    result = crud.get_guild_members(test_db, discord_guild_id=987654321)
    assert len(result) == 3

    result = crud.get_guild_members(test_db, discord_guild_id=111111111)
    assert len(result) == 3

    result = crud.get_guild_members(test_db, discord_guild_id=222222222)
    assert len(result) == 1

    assert isinstance(result[0], models.User)


#
# DISCORD DESTINATIONS
#

# MULTIPLE DESTINATIONS


def test_get_user_destinations_by_user_id(test_db):
    # User 1 should be in 1 guild
    result = crud.get_user_destinations(test_db, user_id=1, discord_user_id=None)
    assert len(result) == 1
    assert result[0].discord_guild_id == 123456789

    # User 2 should be in 2 guilds
    result = crud.get_user_destinations(test_db, user_id=2, discord_user_id=None)
    assert len(result) == 2
    assert result[0].discord_guild_id in [987654321, 111111111]

    # User 3 should be in 3 guilds
    result = crud.get_user_destinations(test_db, user_id=3, discord_user_id=None)
    assert len(result) == 3
    assert result[0].discord_guild_id in [123456789, 987654321, 111111111]

    # User 4 should be in 4 guilds
    result = crud.get_user_destinations(test_db, user_id=4, discord_user_id=None)
    assert len(result) == 4
    assert result[0].discord_guild_id in [123456789, 987654321, 111111111, 222222222]


def test_get_user_destinations_by_discord_user_id(test_db):
    # User 1 should be in 1 guild
    result = crud.get_user_destinations(test_db, user_id=None, discord_user_id=123456789)
    assert len(result) == 1
    assert result[0].discord_guild_id == 123456789

    # User 2 should be in 2 guilds
    result = crud.get_user_destinations(test_db, user_id=None, discord_user_id=987654321)
    assert len(result) == 2
    assert result[0].discord_guild_id in [123456789, 111111111]

    # User 3 should be in 3 guilds
    result = crud.get_user_destinations(test_db, user_id=None, discord_user_id=777777777)
    assert len(result) == 3
    assert result[0].discord_guild_id in [123456789, 987654321, 111111111]

    # User 4 should be in 4 guilds
    result = crud.get_user_destinations(test_db, user_id=None, discord_user_id=888888888)
    assert len(result) == 4
    assert result[0].discord_guild_id in [123456789, 987654321, 111111111, 222222222]


def test_get_user_destinations_by_non_existent_user_id(test_db):
    result = crud.get_user_destinations(test_db, user_id=999, discord_user_id=None)
    assert result is None


def test_get_user_destinations_by_non_existent_discord_user_id(test_db):
    result = crud.get_user_destinations(test_db, user_id=None, discord_user_id=999999999)
    assert result is None


# SINGLE DESTINATION


def test_get_user_destination_by_user_id_user_in_guild(test_db):
    result = crud.get_user_destination(test_db, user_id=1, discord_user_id=None, discord_guild_id=123456789)
    assert result.user_id == 1

    result = crud.get_user_destination(test_db, user_id=2, discord_user_id=None, discord_guild_id=987654321)
    assert result.user_id == 2

    result = crud.get_user_destination(test_db, user_id=3, discord_user_id=None, discord_guild_id=123456789)
    assert result.user_id == 3

    result = crud.get_user_destination(test_db, user_id=4, discord_user_id=None, discord_guild_id=123456789)
    assert result.user_id == 4

    result = crud.get_user_destination(test_db, user_id=4, discord_user_id=None, discord_guild_id=987654321)
    assert result.user_id == 4


def test_get_user_destination_by_user_id_user_not_in_guild(test_db):
    result = crud.get_user_destination(test_db, user_id=1, discord_user_id=None, discord_guild_id=987654321)
    assert result is None

    result = crud.get_user_destination(test_db, user_id=2, discord_user_id=None, discord_guild_id=123456789)
    assert result is None

    result = crud.get_user_destination(test_db, user_id=3, discord_user_id=None, discord_guild_id=222222222)
    assert result is None

    result = crud.get_user_destination(test_db, user_id=4, discord_user_id=None, discord_guild_id=333333333)
    assert result is None


# SET DESTINATION


def test_set_user_destination(test_db):
    # let user 1 be in 5 guilds
    result = crud.set_user_destination(test_db, user_id=1, discord_guild_id=123456789)
    assert result.user_id == 1

    result = crud.set_user_destination(test_db, user_id=1, discord_guild_id=987654321)
    assert result.user_id == 1

    result = crud.set_user_destination(test_db, user_id=1, discord_guild_id=111111111)
    assert result.user_id == 1

    result = crud.set_user_destination(test_db, user_id=1, discord_guild_id=222222222)
    assert result.user_id == 1

    result = crud.set_user_destination(test_db, user_id=1, discord_guild_id=333333333)
    assert result.user_id == 1

    # check if user 1 is in 5 guilds
    result = crud.get_user_destinations(test_db, user_id=1, discord_user_id=None)
    assert len(result) == 5

    for id in range(2, 5):
        result = crud.get_user_destinations(test_db, user_id=id, discord_user_id=None)
        assert len(result) == id


# DELETE DESTINATION


def test_delete_user_destination(test_db):
    # remove 3 guilds from user 1

    result = crud.delete_user_destination(test_db, user_id=1, discord_user_id=None, discord_guild_id=123456789)
    assert result.user_id == 1

    result = crud.delete_user_destination(test_db, user_id=1, discord_user_id=None, discord_guild_id=987654321)
    assert result.user_id == 1

    result = crud.delete_user_destination(test_db, user_id=1, discord_user_id=None, discord_guild_id=111111111)
    assert result.user_id == 1

    result = crud.get_user_destinations(test_db, user_id=1, discord_user_id=None)
    assert len(result) == 2

    for id in range(2, 5):
        result = crud.get_user_destinations(test_db, user_id=id, discord_user_id=None)
        assert len(result) == id


# DELETE DESTINATIONS


def test_delete_user_destinations(test_db):
    # remove all guilds from user 1

    result = crud.delete_user_destinations(test_db, user_id=1, discord_user_id=None)
    assert result == None

    result = crud.get_user_destinations(test_db, user_id=1, discord_user_id=None)
    assert result is None or len(result) == 0

    for id in range(2, 5):
        result = crud.get_user_destinations(test_db, user_id=id, discord_user_id=None)
        assert len(result) == id


#
# FILMWEB MOVIES
#


def test_get_filmweb_movie_by_id(test_db):
    result = crud.get_movie_filmweb_id(test_db, id=628)
    assert result.id == 628
    assert result.title == "Matrix"
    assert result.year == 1999
    assert result.poster_url == "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp"
    assert result.community_rate == 7.7


def test_create_filmweb_movie(test_db):
    movie = models.FilmWebMovie(
        id=999,
        title="Test",
        year=2021,
        poster_url="https://example.com/image.jpg",
        community_rate=9.9,
    )
    result = crud.create_filmweb_movie(test_db, movie)
    assert result.id == 999
    assert result.title == "Test"
    assert result.year == 2021
    assert result.poster_url == "https://example.com/image.jpg"
    assert result.community_rate == 9.9


def test_create_filmweb_movie_existing(test_db):
    movie = models.FilmWebMovie(
        id=628,
        title="Test",
        year=2021,
        poster_url="https://example.com/image.jpg",
        community_rate=9.9,
    )
    result = crud.create_filmweb_movie(test_db, movie)
    assert result.id == 628
    assert result.title == "Matrix"
    assert result.year == 1999
    assert result.poster_url == "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp"
    assert result.community_rate == 7.7


def test_update_filmweb_movie(test_db):
    movie = models.FilmWebMovie(
        id=628,
        title="Test number 2",
        year=2022,
        poster_url="https://example.com/image2.jpg",
        community_rate=8.8,
    )

    result = crud.update_filmweb_movie(test_db, movie)
    assert result.id == 628
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.poster_url == "https://example.com/image2.jpg"
    assert result.community_rate == 8.8

    result = crud.get_movie_filmweb_id(test_db, id=628)
    assert result.id == 628
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.poster_url == "https://example.com/image2.jpg"
    assert result.community_rate == 8.8


#
# FILMWEB SERIES
#


def test_get_filmweb_series_by_id(test_db):
    result = crud.get_series_filmweb_id(test_db, id=430668)
    assert result.id == 430668
    assert result.title == "Breaking Bad"
    assert result.year == 2008
    assert result.other_year == 2013
    assert result.poster_url == "https://fwcdn.pl/fpo/06/68/430668/7730445_2.10.webp"
    assert result.community_rate == 8.8


def test_create_filmweb_series(test_db):
    series = models.FilmWebSeries(
        id=999,
        title="Test",
        year=2021,
        other_year=2022,
        poster_url="https://example.com/image.jpg",
        community_rate=9.9,
    )
    result = crud.create_filmweb_series(test_db, series)
    assert result.id == 999
    assert result.title == "Test"
    assert result.year == 2021
    assert result.other_year == 2022
    assert result.poster_url == "https://example.com/image.jpg"
    assert result.community_rate == 9.9


def test_create_filmweb_series_existing(test_db):
    series = models.FilmWebSeries(
        id=430668,
        title="Test",
        year=2021,
        other_year=2022,
        poster_url="https://example.com/image.jpg",
        community_rate=9.9,
    )
    result = crud.create_filmweb_series(test_db, series)
    assert result.id == 430668
    assert result.title == "Breaking Bad"
    assert result.year == 2008
    assert result.other_year == 2013
    assert result.poster_url == "https://fwcdn.pl/fpo/06/68/430668/7730445_2.10.webp"
    assert result.community_rate == 8.8


def test_update_filmweb_series(test_db):
    series = models.FilmWebSeries(
        id=430668,
        title="Test number 2",
        year=2022,
        other_year=2023,
        poster_url="https://example.com/image2.jpg",
        community_rate=5.8,
    )

    result = crud.update_filmweb_series(test_db, series)
    assert result.id == 430668
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.other_year == 2023
    assert result.poster_url == "https://example.com/image2.jpg"
    assert result.community_rate == 5.8

    result = crud.get_series_filmweb_id(test_db, id=430668)
    assert result.id == 430668
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.other_year == 2023
    assert result.poster_url == "https://example.com/image2.jpg"
    assert result.community_rate == 5.8


#
# FILMWEB MAPPINGS
#


def test_get_filmweb_mapping_no_parameters(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is None


def test_set_filmweb_mapping(test_db):
    mapping = models.FilmWebUserMapping(
        user_id=3,
        filmweb_id="test123",
    )

    result = crud.set_filmweb_user_mapping(test_db, mapping)
    assert result.user_id == 3
    assert result.filmweb_id == "test123"

    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert result.user_id == 3
    assert result.filmweb_id == "test123"


def test_set_filmweb_mapping2(test_db):
    # user 1 should not have mapping anymore
    mapping = models.FilmWebUserMapping(
        user_id=1,
        filmweb_id="HELLO_WORLD",
    )

    result = crud.set_filmweb_user_mapping(test_db, mapping)
    assert result.user_id == 1
    assert result.filmweb_id == "HELLO_WORLD"

    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=1,
        filmweb_id=None,
        discord_id=None,
    )

    assert result.user_id == 1
    assert result.filmweb_id == "HELLO_WORLD"


def test_get_filmweb_mapping_by_user_id(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=2,
        filmweb_id=None,
        discord_id=None,
    )

    assert result.user_id == 2
    assert result.filmweb_id == "filmweb123"


def test_get_filmweb_mapping_by_filmweb_id(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=None,
        filmweb_id="filmweb123",
        discord_id=None,
    )

    assert result.user_id == 2
    assert result.filmweb_id == "filmweb123"


def test_get_filmweb_mapping_by_discord_id(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=987654321,
    )

    assert result.user_id == 2
    assert result.filmweb_id == "filmweb123"


# user 2 should not have mapping anymore
def test_delete_filmweb_mapping(test_db):

    result = crud.delete_filmweb_user_mapping(
        test_db,
        user_id=2,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is True

    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=2,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is None


def test_get_filmweb_mapping_by_user_id2(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert result.user_id == 3
    assert result.filmweb_id == "test123"


def test_get_filmweb_mapping_by_filmweb_id2(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert result.user_id == 3
    assert result.filmweb_id == "test123"


def test_get_filmweb_mapping_by_discord_id2(test_db):
    result = crud.get_filmweb_user_mapping(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=777777777,
    )

    assert result.user_id == 3
    assert result.filmweb_id == "test123"


#
# FILMWEB WATCHED MOVIES
#


def test_create_filmweb_watched_movie(test_db):
    watched_movie = models.FilmWebUserWatchedMovie(
        id_media=628,
        filmweb_id="test123",
        date=datetime.datetime(2021, 1, 1, 18, 23, 43),
        rate=5,
        comment="Test",
        favorite=True,
    )

    result = crud.create_filmweb_user_watched_movie(test_db, watched_movie)
    assert result.id_media == 628
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2021, 1, 1, 18, 23, 43)
    assert result.rate == 5
    assert result.comment == "Test"
    assert result.favorite == True

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert len(result) == 1

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 1

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=777777777,
    )

    assert len(result) == 1


def test_get_filmweb_watched_movie_by_id(test_db):
    result = crud.get_filmweb_user_watched_movie(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
        id_media=628,
    )

    assert result.id_media == 628
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2021, 1, 1, 18, 23, 43)
    assert result.rate == 5
    assert result.comment == "Test"
    assert result.favorite == True


def test_get_filmweb_watched_movie_by_id_no_existing(test_db):
    result = crud.get_filmweb_user_watched_movie(
        test_db,
        id_media=999,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert result is None


def test_create_filmweb_watched_movie_no_existing(test_db):
    watched_movie = models.FilmWebUserWatchedMovie(
        id_media=100001,
        filmweb_id="test123",
        date=datetime.datetime(2023, 4, 6, 12, 53, 12),
        rate=8,
        comment="Test",
        favorite=False,
    )

    result = crud.create_filmweb_user_watched_movie(test_db, watched_movie)
    assert result.id_media == 100001
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2023, 4, 6, 12, 53, 12)
    assert result.rate == 8
    assert result.comment == "Test"
    assert result.favorite == False

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=777777777,
    )

    assert len(result) == 2

    result = crud.get_movie_filmweb_id(test_db, id=100001)
    assert result.id == 100001
    assert result.title == None
    assert result.year == None
    assert result.poster_url == None
    assert result.community_rate == None

    # other movie should be still in db
    result = crud.get_movie_filmweb_id(test_db, id=628)
    assert result.id == 628
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.poster_url == "https://example.com/image2.jpg"
    assert result.community_rate == 8.8


def test_get_filmweb_user_watched_movies_by_user_id(test_db):
    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=4,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is None

def test_delete_filmweb_watched_movies(test_db):
    result = crud.delete_filmweb_user_watched_movies(
        test_db,
        user_id=1,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is True

    # check length of watched movies
    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=1,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 0

    # check if other users still have watched movies
    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 2

    # and now delete all watched movies for user 3

    result = crud.delete_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    #
    #  TODO: DO SAME FOR SERIES
    #


    assert result is True

    # check length of watched movies

    result = crud.get_filmweb_user_watched_movies(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 0
#
# FILMWEB WATCHED SERIES
#


def test_create_filmweb_watched_series(test_db):
    watched_series = models.FilmWebUserWatchedSeries(
        id_media=430668,
        filmweb_id="test123",
        date=datetime.datetime(2021, 1, 1, 18, 23, 43),
        rate=5,
        comment="Test",
        favorite=True,
    )

    result = crud.create_filmweb_user_watched_series(test_db, watched_series)
    assert result.id_media == 430668
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2021, 1, 1, 18, 23, 43)
    assert result.rate == 5
    assert result.comment == "Test"
    assert result.favorite == True

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert len(result) == 1

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 1

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=777777777,
    )

    assert len(result) == 1


def test_get_filmweb_watched_series_by_id(test_db):
    result = crud.get_filmweb_user_watched_series(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
        id_media=430668,
    )

    assert result.id_media == 430668
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2021, 1, 1, 18, 23, 43)
    assert result.rate == 5
    assert result.comment == "Test"
    assert result.favorite == True


def test_get_filmweb_watched_series_by_id_no_existing(test_db):
    result = crud.get_filmweb_user_watched_series(
        test_db,
        id_media=999,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert result is None


def test_create_filmweb_watched_series_no_existing(test_db):
    watched_series = models.FilmWebUserWatchedSeries(
        id_media=100001,
        filmweb_id="test123",
        date=datetime.datetime(2023, 4, 6, 12, 53, 12),
        rate=8,
        comment="Test",
        favorite=False,
    )

    result = crud.create_filmweb_user_watched_series(test_db, watched_series)
    assert result.id_media == 100001
    assert result.filmweb_id == "test123"
    assert result.date == datetime.datetime(2023, 4, 6, 12, 53, 12)
    assert result.rate == 8
    assert result.comment == "Test"
    assert result.favorite == False

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=None,
        filmweb_id="test123",
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=None,
        filmweb_id=None,
        discord_id=777777777,
    )

    assert len(result) == 2

    result = crud.get_series_filmweb_id(test_db, id=100001)
    assert result.id == 100001
    assert result.title == None
    assert result.year == None
    assert result.other_year == None
    assert result.poster_url == None

    # other series should be still in db
    result = crud.get_series_filmweb_id(test_db, id=430668)
    assert result.id == 430668
    assert result.title == "Test number 2"
    assert result.year == 2022
    assert result.other_year == 2023
    assert result.poster_url == "https://example.com/image2.jpg"


def test_get_filmweb_user_watched_series_all_by_user_id(test_db):
    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=3,
        filmweb_id=None,
        discord_id=None,
    )

    assert len(result) == 2

    result = crud.get_filmweb_user_watched_series_all(
        test_db,
        user_id=4,
        filmweb_id=None,
        discord_id=None,
    )

    assert result is None
