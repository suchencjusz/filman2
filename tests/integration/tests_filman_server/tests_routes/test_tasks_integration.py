import logging
import responses
import time

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from filman_server.database import models, schemas
from filman_server.database.db import Base, get_db
from filman_server.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # memory db is not working for some reason
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# TestingSessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close_all()


app.dependency_overrides[get_db] = override_get_db

models.Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="module")
def test_client():
    yield client

@pytest.fixture(autouse=True)
def clear_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Nomral task creation process
# /tasks/create
def test_create_task(test_client: TestClient):
    task_data = {
        "task_status": "queued",
        "task_type": "scrap_filmweb_user",
        "task_job": "sample_user",
        "task_created": "2021-01-01T00:00:00",
        "task_started": "2021-01-01T00:00:00",
        "task_finished": "2021-01-01T00:00:00",
    }

    response = test_client.post("/tasks/create", json=task_data)

    assert response.status_code == 200

    task = response.json()

    assert task["task_id"] is not None
    assert task["task_status"] == task_data["task_status"]
    assert task["task_type"] == task_data["task_type"]
    assert task["task_job"] == task_data["task_job"]
    assert task["task_created"] is not None


# Test task creation and retrieval if there is any task to do (without doing the task)
# head /tasks/get/to_do
def test_tasks_to_do_head(test_client: TestClient):
    task_data_list = [
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_user",
            "task_job": "sample_user",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_movie",
            "task_job": "283",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_user_watched_series",
            "task_job": "sample_user",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
    ]

    for task_data in task_data_list:
        response = test_client.post("/tasks/create", json=task_data)
        assert response.status_code == 200

    task_types_and_status_codes = [
        (["scrap_filmweb_user"], 200),
        (["scrap_filmweb_movie"], 200),
        (["scrap_filmweb_user_watched_series"], 200),
        (["scrap_filmweb_user_watched_series", "scrap_filmweb_movie"], 200),
        (["scrap_filmweb_user", "scrap_filmweb_movie", "scrap_filmweb_user_watched_series"], 200),
        (["scrap_filmweb_user", "scrap_filmweb_movie", "scrap_filmweb_user_watched_series", "scrap_filmweb_series"], 200),
        ([], 422),
        ([""], 422),
        (["hello"], 422),
        (["scrap_filmweb_user_watched_movies"], 404),
        (["scrap_filmweb_series", "scrap_filmweb_user_watched_movies"], 404),
    ]

    for task_types, expected_status in task_types_and_status_codes:
        response = test_client.head("/tasks/get/to_do", params={"task_types": task_types})
        assert response.status_code == expected_status


# get /tasks/get/to_do
def test_tasks_to_do_get(test_client: TestClient):
    task_data_list = [
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_user",
            "task_job": "sample_user",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_movie",
            "task_job": "283",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
        {
            "task_status": "queued",
            "task_type": "scrap_filmweb_user_watched_series",
            "task_job": "sample_user",
            "task_created": "2021-01-01T00:00:00",
            "task_started": "2021-01-01T00:00:00",
            "task_finished": "2021-01-01T00:00:00",
        },
    ]

    for task_data in task_data_list:
        response = test_client.post("/tasks/create", json=task_data)
        assert response.status_code == 200

    for task_data in task_data_list:
        response = test_client.get("/tasks/get/to_do", params={"task_types": [task_data["task_type"]]})
        assert response.status_code == 200

        task = response.json()

        assert task["task_id"] > 0
        assert [task["task_status"] in schemas.TaskStatus.__members__]
        assert task["task_type"] == task_data["task_type"]
        assert task["task_job"] == task_data["task_job"]
        assert task["task_created"] is not None


# get /tasks/create
def test_task_update_task_status(test_client: TestClient):
    task_data = {
        "task_status": "queued",
        "task_type": "scrap_filmweb_user",
        "task_job": "sample_user",
        "task_created": "2021-01-01T00:00:00",
        "task_started": "2021-01-01T00:00:00",
        "task_finished": "2021-01-01T00:00:00",
    }

    response = test_client.post("/tasks/create", json=task_data)
    task = response.json()

    assert response.status_code == 200

    logging.debug(task)

    task_status_all = list(schemas.TaskStatus.__members__.items())

    logging.debug(task_status_all)

    for task_status in task_status_all:

        logging.info(f"Updating task status to (id: {task['task_id']}, status: {task_status[1].value})")

        response = test_client.get(f"/tasks/update/status/{task['task_id']}/{task_status[1].value}")
        assert response.status_code == 200

        updated_task = response.json()

        assert updated_task["task_id"] == task["task_id"]
        assert updated_task["task_status"] == task_status[1].value
        assert updated_task["task_type"] == task["task_type"]
        assert updated_task["task_job"] == task["task_job"]
        assert updated_task["task_created"] == task["task_created"]
        # i do not know how to test task_started and task_finished + nobody cares about them, it is only for stats.


# get /tasks/new/scrap/filmweb/users/movies
def test_tasks_new_scrap_filmweb_users_movies(test_client: TestClient):
    response = test_client.get("/tasks/new/scrap/filmweb/users/movies")
    assert response.status_code == 200

    assert response.json() is True

    # check if there are any tasks in the database
    response = test_client.head("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_user"]})
    assert response.status_code == 404

    # create users and filmweb mappings
    test_users = [
        {"discord_id": 128903712},
        {"discord_id": 128903713},
        {"discord_id": 128903714},
        {"discord_id": 128903715},
    ]

    test_filmweb_nicknames = [
        "arek",
        "marek",
        "darek",
        "jarek",
    ]

    # create users
    for user in test_users:
        response = test_client.post("/users/create", json=user)
        assert response.status_code == 200

        # map users to filmweb ids
    for filmweb_id, user_id in zip(test_filmweb_nicknames, [1, 2, 3, 4]):
        response = test_client.post("/filmweb/user/mapping/set", json={"user_id": user_id, "filmweb_id": filmweb_id})
        assert response.status_code == 200

    response = test_client.get("/tasks/new/scrap/filmweb/users/movies")
    assert response.status_code == 200
    assert response.json() is True

    response = test_client.head("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_user_watched_movies"]})
    assert response.status_code == 200

    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_user_watched_movies"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 1
        assert response.json()["task_status"] == "running"
        assert response.json()["task_type"] == "scrap_filmweb_user_watched_movies"
        assert response.json()["task_job"] == "arek"
        assert response.json()["task_created"] is not None
        assert response.json()["task_started"] is not None

        frozen_time.tick(delta=61)

        response = test_client.get("/tasks/update/stuck/1")
        assert response.status_code == 200
        assert response.json() is True

        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_user_watched_movies"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 1

        frozen_time.tick(delta=61)

        response = test_client.get("/tasks/update/old/1")
        assert response.status_code == 200
        assert response.json() is True

        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_user_watched_movies"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 2


# get /tasks/new/scrap/filmweb/movies
def test_tasks_new_scrap_filmweb_movies(test_client: TestClient):

    response = test_client.get("/tasks/new/scrap/filmweb/movies")
    assert response.status_code == 200

    assert response.json() is True

    # check if there are any tasks in the database
    response = test_client.head("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_movie"]})
    assert response.status_code == 404

    # add some movies to fimweb database
    test_movies_data = [
        {
            "id": 628,
            "title": "Matrix",
            "year": 1999,
            "poster_url": "https://fwcdn.pl/fpo/06/28/628/7685907_1.10.webp",
            "community_rate": 7.6,
            "critics_rate": 8.0,
        },
        {
            "id": 1,
            "title": "Paragraf 187",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/01/1/7418875_1.10.webp",
            "community_rate": 7.3,
            "critics_rate": 7.0,
        },
        {
            "id": 2,
            "title": "Adwokat diabła",
            "year": 1997,
            "poster_url": "https://fwcdn.pl/fpo/00/02/2/6956729_1.10.webp",
            "community_rate": 7.9,
            "critics_rate": 7.0,
        },
    ]

    for movie in test_movies_data:
        response = test_client.post("/filmweb/movie/update", json=movie)
        assert response.status_code == 200
        assert response.json() == movie

    response = test_client.get("/tasks/new/scrap/filmweb/movies")
    assert response.status_code == 200
    assert response.json() is True

    response = test_client.head("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_movie"]})
    assert response.status_code == 200

    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_movie"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 1
        assert response.json()["task_status"] == "running"
        assert response.json()["task_type"] == "scrap_filmweb_movie"
        assert response.json()["task_job"] == "1"
        assert response.json()["task_created"] is not None
        assert response.json()["task_started"] is not None

        frozen_time.tick(delta=61)

        response = test_client.get("/tasks/update/stuck/1")
        assert response.status_code == 200
        assert response.json() is True

        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_movie"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 1

        frozen_time.tick(delta=61)

        response = test_client.get("/tasks/update/old/1")
        assert response.status_code == 200
        assert response.json() is True

        response = test_client.get("/tasks/get/to_do", params={"task_types": ["scrap_filmweb_movie"]})
        assert response.status_code == 200
        assert response.json()["task_id"] == 2
