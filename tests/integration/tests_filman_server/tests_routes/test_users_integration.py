import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filman_server.database import models
from filman_server.database.db import Base, get_db
from filman_server.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

models.Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="module")
def test_client():
    yield client


@pytest.fixture(autouse=True)
def clear_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Create 5 users and get them by id
# get /users/get
def test_get_user(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
        {"discord_id": 321309474367253285},
        {"discord_id": 321309474467253286},
    ]

    # create users
    for user_data in test_users_data:
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["id"] > 0
        assert user["discord_id"] == user_data["discord_id"]

    # get by id
    for user_data, id in zip(test_users_data, range(1, 6)):
        response = test_client.get(f"/users/get", params={"user_id": id})
        assert response.status_code == 200

        user = response.json()

        assert user["id"] == id
        assert user["discord_id"] == user_data["discord_id"]

    # create user which exists
    response = test_client.post("/users/create", json=test_users_data[0])
    assert response.status_code == 202

    # check using other endpoint /get_all
    response = test_client.get("/users/get_all")
    assert response.status_code == 200
    assert len(response.json()) == 5


# Create 3 guilds, 15 users and add them to guild, and check if they are in guild
# get /users/add_to_guild
def test_add_user_to_guild(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
        {"discord_id": 321309474367253285},
        {"discord_id": 321309474467253286},
        {"discord_id": 321309474567253287},
        {"discord_id": 321309474667253288},
        {"discord_id": 321309474767253289},
        {"discord_id": 321309474867253290},
        {"discord_id": 321309474967253291},
        {"discord_id": 321309474067253292},
        {"discord_id": 321309474167253293},
        {"discord_id": 321309474267253294},
        {"discord_id": 321309474367253295},
        {"discord_id": 321309474467253296},
    ]

    test_discord_guilds_data = [
        {
            "discord_guild_id": 1209989703772799056,
            "discord_channel_id": 132632676225122304,
        },
        {
            "discord_guild_id": 1209989703772799057,
            "discord_channel_id": 132632676225122305,
        },
        {
            "discord_guild_id": 1209989703772799058,
            "discord_channel_id": 132632676225122306,
        },
    ]

    # create users
    for user_data, id in zip(test_users_data, range(1, 16)):
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["id"] == id
        assert user["discord_id"] == user_data["discord_id"]

    # create guilds
    for guild_data, id in zip(test_discord_guilds_data, range(1, 4)):
        response = test_client.post("/discord/configure/guild", json=guild_data)
        assert response.status_code == 200

        guild = response.json()

        assert guild["id"] == id
        assert guild["discord_guild_id"] == guild_data["discord_guild_id"]
        assert guild["discord_channel_id"] == guild_data["discord_channel_id"]

    # check if guilds are really in database
    response = test_client.get("/discord/guilds")
    assert response.status_code == 200

    guilds = response.json()
    assert len(guilds) == 3


# Remove user from guild
# get /users/remove_from_guild
def test_remove_user_from_guild(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
        {"discord_id": 321309474367253285},
        {"discord_id": 321309474467253286},
    ]

    test_discord_guilds_data = [
        {
            "discord_guild_id": 1209989703772799056,
            "discord_channel_id": 132632676225122304,
        },
        {
            "discord_guild_id": 1209989703772799057,
            "discord_channel_id": 132632676225122305,
        },
        {
            "discord_guild_id": 1209989703772799058,
            "discord_channel_id": 132632676225122306,
        },
    ]

    # create users
    for user_data, id in zip(test_users_data, range(1, 6)):
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["id"] == id
        assert user["discord_id"] == user_data["discord_id"]

    # create guilds
    for guild_data, id in zip(test_discord_guilds_data, range(1, 4)):
        response = test_client.post("/discord/configure/guild", json=guild_data)
        assert response.status_code == 200

        guild = response.json()

        assert guild["id"] == id
        assert guild["discord_guild_id"] == guild_data["discord_guild_id"]
        assert guild["discord_channel_id"] == guild_data["discord_channel_id"]

    # add all users to all guilds
    for user_data in test_users_data:
        for guild_data in test_discord_guilds_data:
            response = test_client.get(
                f"/users/add_to_guild",
                params={
                    "discord_id": user_data["discord_id"],
                    "discord_guild_id": guild_data["discord_guild_id"],
                },
            )
            assert response.status_code == 200

            discord_destination = response.json()

            assert discord_destination["user_id"] > 0
            assert discord_destination["discord_guild_id"] == guild_data["discord_guild_id"]

    # check channels of user nr 1
    response = test_client.get("/users/get_all_channels", params={"user_id": 1})
    assert response.status_code == 200
    assert len(response.json()) == 3

    # check guild members
    response = test_client.get(
        f"/discord/guild/members",
        params={"discord_guild_id": test_discord_guilds_data[0]["discord_guild_id"]},
    )
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert isinstance(response.json(), list)
    assert isinstance(response.json()[0], dict)  # idk how to check if it is a "user"

    # remove user nr 1 from guild nr 1
    response = test_client.delete(
        f"/users/remove_from_guild",
        params={
            "discord_user_id": test_users_data[0]["discord_id"],
            "discord_guild_id": test_discord_guilds_data[0]["discord_guild_id"],
        },
    )
    assert response.status_code == 200

    # check if user is not in guild
    response = test_client.get(
        f"/discord/guild/members",
        params={"discord_guild_id": test_discord_guilds_data[0]["discord_guild_id"]},
    )
    assert response.status_code == 200

    guild_members = response.json()
    assert len(guild_members) == 4
    assert [test_users_data[0]["discord_id"]] not in [member["discord_id"] for member in guild_members]


# Remove user from all guilds
# get /users/remove_from_all_guilds
def test_remove_user_from_all_guilds(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
        {"discord_id": 321309474367253285},
        {"discord_id": 321309474467253286},
    ]

    test_discord_guilds_data = [
        {
            "discord_guild_id": 1209989703772799056,
            "discord_channel_id": 132632676225122304,
        },
        {
            "discord_guild_id": 1209989703772799057,
            "discord_channel_id": 132632676225122305,
        },
        {
            "discord_guild_id": 1209989703772799058,
            "discord_channel_id": 132632676225122306,
        },
    ]

    # create users
    for user_data, id in zip(test_users_data, range(1, 6)):
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["id"] == id
        assert user["discord_id"] == user_data["discord_id"]

    # create guilds
    for guild_data, id in zip(test_discord_guilds_data, range(1, 4)):
        response = test_client.post("/discord/configure/guild", json=guild_data)
        assert response.status_code == 200

        guild = response.json()

        assert guild["id"] == id
        assert guild["discord_guild_id"] == guild_data["discord_guild_id"]
        assert guild["discord_channel_id"] == guild_data["discord_channel_id"]

    # add all users to all guilds
    for user_data in test_users_data:
        for guild_data in test_discord_guilds_data:
            response = test_client.get(
                f"/users/add_to_guild",
                params={
                    "discord_id": user_data["discord_id"],
                    "discord_guild_id": guild_data["discord_guild_id"],
                },
            )
            assert response.status_code == 200

            discord_destination = response.json()

            assert discord_destination["user_id"] > 0
            assert discord_destination["discord_guild_id"] == guild_data["discord_guild_id"]

    # check guild members
    response = test_client.get(
        f"/discord/guild/members",
        params={"discord_guild_id": test_discord_guilds_data[0]["discord_guild_id"]},
    )
    assert response.status_code == 200
    assert len(response.json()) == 5

    # remove user nr 1 from all guilds
    response = test_client.delete(
        f"/users/remove_from_all_guilds",
        params={"discord_user_id": test_users_data[0]["discord_id"]},
    )
    assert response.status_code == 200

    # check if user is not in this guild
    response = test_client.get(
        f"/discord/guild/members",
        params={"discord_guild_id": test_discord_guilds_data[0]["discord_guild_id"]},
    )

    assert response.status_code == 200
    assert [test_users_data[0]["discord_id"]] not in [member["discord_id"] for member in response.json()]

    # check using other endpoint
    response = test_client.get("/users/get_all_guilds", params={"discord_id": test_users_data[0]["discord_id"]})
    assert response.status_code == 404
