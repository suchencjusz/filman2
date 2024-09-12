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


# create 3 movies
# post /filmweb/update/movie
def test_update_movie(test_client):
    test_movies_data = [
        {
            "id": 628,
            "title": "Matrix",
            "year": 1999,
            "poster_url": "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp",
            "community_rate": 7.6,
        },
        {
            "id": 1,
            "title": "Paragraf 187",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/01/1/7418875_1.10.webp",
            "community_rate": 7.3,
        },
        {
            "id": 2,
            "title": "Adwokat diabła",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/02/2/6956729_1.10.webp",
            "community_rate": 7.9,
        },
    ]

    for movie in test_movies_data:
        response = test_client.post("/filmweb/movie/update", json=movie)
        assert response.status_code == 200
        assert response.json() == movie


# add watched movie for user
def test_add_watched_movie(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
    ]

    test_users_filmweb_ids = [
        "maciek",
        "steafan",
        "albert",
    ]

    test_movies_data = [
        {
            "id": 628,
            "title": "Matrix",
            "year": 1999,
            "poster_url": "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp",
            "community_rate": 7.6,
        },
        {
            "id": 1,
            "title": "Paragraf 187",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/01/1/7418875_1.10.webp",
            "community_rate": 7.3,
        },
        {
            "id": 2,
            "title": "Adwokat diabła",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/02/2/6956729_1.10.webp",
            "community_rate": 7.9,
        },
    ]

    for movie in test_movies_data:
        response = test_client.post("/filmweb/movie/update", json=movie)
        assert response.status_code == 200
        assert response.json() == movie

    # create users
    for user_data in test_users_data:
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["discord_id"] == user_data["discord_id"]

    # map users to filmweb ids
    for filweb_id, user_id in zip(test_users_filmweb_ids, [1, 2, 3]):
        response = test_client.post("/filmweb/user/mapping/set", json={"user_id": user_id, "filmweb_id": filweb_id})
        assert response.status_code == 200

    # check user mappings via ids
    for user_id, filmweb_id in zip([1, 2, 3], test_users_filmweb_ids):
        response = test_client.get("/filmweb/user/mapping/get", params={"user_id": user_id})
        assert response.status_code == 200
        assert response.json()["filmweb_id"] == filmweb_id

    # check user mappings via filmweb ids
    for user_id, filmweb_id in zip([1, 2, 3], test_users_filmweb_ids):
        response = test_client.get("/filmweb/user/mapping/get", params={"filmweb_id": filmweb_id})
        assert response.status_code == 200
        assert response.json()["user_id"] == user_id

    # check user mappings via discord ids
    for user_id, discord_id in zip([1, 2, 3], [321309474667253282, 321309474167253283, 321309474267253284]):
        response = test_client.get("/filmweb/user/mapping/get", params={"discord_id": discord_id})
        assert response.status_code == 200
        assert response.json()["user_id"] == user_id

    # let user 1 watch 1 of the movies
    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 628,
            "filmweb_id": "maciek",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 7,
            "comment": "good movie",
            "favorite": False,
        },
    )
    assert response.status_code == 200

    # check if the movie was added to the watched movies
    response = test_client.get("/filmweb/user/watched/movies/get", params={"user_id": 1})
    assert response.status_code == 200
    assert response.json()[0]["movie"]["id"] == 628
    assert response.json()[0]["rate"] == 7
    assert response.json()[0]["comment"] == "good movie"
    assert response.json()[0]["favorite"] == False

    # let user 2 watch 2 of the movies
    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 1,
            "filmweb_id": "steafan",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 5,
            "comment": None,
            "favorite": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["id_media"] == 1
    assert response.json()["filmweb_id"] == "steafan"
    assert response.json()["rate"] == 5
    assert response.json()["comment"] == None
    assert response.json()["favorite"] == False

    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 2,
            "filmweb_id": "steafan",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 2,
            "comment": "awesome",
            "favorite": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["id_media"] == 2
    assert response.json()["filmweb_id"] == "steafan"
    assert response.json()["rate"] == 2
    assert response.json()["comment"] == "awesome"
    assert response.json()["favorite"] == True

    # check if the movies were added to the watched movies
    response = test_client.get("/filmweb/user/watched/movies/get", params={"user_id": 2})
    assert response.status_code == 200
    assert response.json()[0]["movie"]["id"] == 1
    assert response.json()[0]["rate"] == 5
    assert response.json()[0]["comment"] == None
    assert response.json()[0]["favorite"] == False

    assert response.json()[1]["movie"]["id"] == 2
    assert response.json()[1]["rate"] == 2
    assert response.json()[1]["comment"] == "awesome"
    assert response.json()[1]["favorite"] == True

    # let user 3 watch 3 of the movies
    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 628,
            "filmweb_id": "albert",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 7,
            "comment": "good movie",
            "favorite": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["id_media"] == 628
    assert response.json()["filmweb_id"] == "albert"
    assert response.json()["rate"] == 7
    assert response.json()["comment"] == "good movie"
    assert response.json()["favorite"] == False

    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 1,
            "filmweb_id": "albert",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 5,
            "comment": None,
            "favorite": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["id_media"] == 1
    assert response.json()["filmweb_id"] == "albert"
    assert response.json()["rate"] == 5
    assert response.json()["comment"] == None
    assert response.json()["favorite"] == False

    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 2,
            "filmweb_id": "albert",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 2,
            "comment": "awesome",
            "favorite": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["id_media"] == 2
    assert response.json()["filmweb_id"] == "albert"
    assert response.json()["rate"] == 2
    assert response.json()["comment"] == "awesome"
    assert response.json()["favorite"] == True

    # check if the movies were added to the watched movies
    response = test_client.get("/filmweb/user/watched/movies/get", params={"user_id": 3})
    assert response.status_code == 200
    assert response.json()[0]["movie"]["id"] == 628
    assert response.json()[0]["rate"] == 7
    assert response.json()[0]["comment"] == "good movie"
    assert response.json()[0]["favorite"] == False

    assert response.json()[1]["movie"]["id"] == 1
    assert response.json()[1]["rate"] == 5
    assert response.json()[1]["comment"] == None
    assert response.json()[1]["favorite"] == False

    assert response.json()[2]["movie"]["id"] == 2
    assert response.json()[2]["rate"] == 2
    assert response.json()[2]["comment"] == "awesome"
    assert response.json()[2]["favorite"] == True

    # let user 1 watch 1 of the movies which does not exist
    response = test_client.post(
        "/filmweb/user/watched/movies/add",
        json={
            "id_media": 3,
            "filmweb_id": "maciek",
            "date": "2024-09-11T20:21:58.072Z",
            "rate": 7,
            "comment": "good movie",
            "favorite": False,
        },
    )
    assert response.status_code == 200

    # check if the movie was added to the watched movies
    response = test_client.get("/filmweb/user/watched/movies/get", params={"user_id": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_user_mapping_delete(test_client):
    test_users_data = [
        {"discord_id": 321309474667253282},
        {"discord_id": 321309474167253283},
        {"discord_id": 321309474267253284},
    ]

    test_users_filmweb_ids = [
        "maciek",
        "steafan",
        "albert",
    ]

    test_movies_data = [
        {
            "id": 628,
            "title": "Matrix",
            "year": 1999,
            "poster_url": "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp",
            "community_rate": 7.6,
        },
        {
            "id": 1,
            "title": "Paragraf 187",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/01/1/7418875_1.10.webp",
            "community_rate": 7.3,
        },
        {
            "id": 2,
            "title": "Adwokat diabła",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/02/2/6956729_1.10.webp",
            "community_rate": 7.9,
        },
    ]

    for movie in test_movies_data:
        response = test_client.post("/filmweb/movie/update", json=movie)
        assert response.status_code == 200
        assert response.json() == movie

    # create users
    for user_data in test_users_data:
        response = test_client.post("/users/create", json=user_data)
        assert response.status_code == 200

        user = response.json()

        assert user["discord_id"] == user_data["discord_id"]

    # map users to filmweb ids
    for filweb_id, user_id in zip(test_users_filmweb_ids, [1, 2, 3]):
        response = test_client.post("/filmweb/user/mapping/set", json={"user_id": user_id, "filmweb_id": filweb_id})
        assert response.status_code == 200

    # check user mappings via ids
    for user_id, filmweb_id in zip([1, 2, 3], test_users_filmweb_ids):
        response = test_client.get("/filmweb/user/mapping/get", params={"user_id": user_id})
        assert response.status_code == 200
        assert response.json()["filmweb_id"] == filmweb_id

    # remove user 1 mapping
    response = test_client.delete("/filmweb/user/mapping/delete", params={"user_id": 1})
    assert response.status_code == 200

    # check user 1 watched movies
    response = test_client.get("/filmweb/user/watched/movies/get", params={"user_id": 1})
    assert response.status_code == 404
