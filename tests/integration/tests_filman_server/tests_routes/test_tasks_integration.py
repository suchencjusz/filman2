import logging
import time
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filman_server.database import models, schemas
from filman_server.database.db import Base, get_db
from filman_server.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # memory db is not working for some reason
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


# Mock Celery task for testing
@pytest.fixture
def mock_celery_task():
    with patch("filman_server.routes.tasks.scrap_movie.delay") as mock:
        mock_task = Mock()
        mock_task.id = "test-task-id-123"
        mock.return_value = mock_task
        yield mock


# Test task creation with Celery
def test_create_task(test_client: TestClient, mock_celery_task):
    task_data = {
        "task_status": "queued",
        "task_type": "scrap_filmweb_user",
        "task_job": "sample_user",
    }

    response = test_client.post("/tasks/create", json=task_data)

    assert response.status_code == 200

    task = response.json()

    assert task["celery_task_id"] == "test-task-id-123"
    assert task["status"] == "queued"
    assert task["task_type"] == task_data["task_type"]
    assert task["task_job"] == task_data["task_job"]
    assert task["message"] == "Task sent to Celery queue successfully"

    # Verify Celery task was called
    mock_celery_task.assert_called_once_with(task_data["task_type"], task_data["task_job"])


# get /tasks/new/scrap/filmweb/users/movies
def test_tasks_new_scrap_filmweb_users_movies(test_client: TestClient, mock_celery_task):
    # Initially, no users exist, so no tasks should be created
    response = test_client.get("/tasks/new/scrap/filmweb/users/movies")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["tasks_queued"] == 0

    # Create users and filmweb mappings
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

    # Create users
    for user in test_users:
        response = test_client.post("/users/create", json=user)
        assert response.status_code == 200

    # Map users to filmweb ids
    for filmweb_id, user_id in zip(test_filmweb_nicknames, [1, 2, 3, 4]):
        response = test_client.post(
            "/filmweb/user/mapping/set",
            json={"user_id": user_id, "filmweb_id": filmweb_id},
        )
        assert response.status_code == 200

    # Now create tasks for all users
    mock_celery_task.reset_mock()
    response = test_client.get("/tasks/new/scrap/filmweb/users/movies")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["tasks_queued"] == 4
    assert len(result["celery_task_ids"]) == 4
    assert mock_celery_task.call_count == 4


# get /tasks/new/scrap/filmweb/movies
def test_tasks_new_scrap_filmweb_movies(test_client: TestClient, mock_celery_task):
    # Initially, no movies exist
    response = test_client.get("/tasks/new/scrap/filmweb/movies")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["tasks_queued"] == 0

    # Add some movies to filmweb database
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

    # Now create tasks for all movies
    mock_celery_task.reset_mock()
    response = test_client.get("/tasks/new/scrap/filmweb/movies")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["tasks_queued"] == 3
    assert len(result["celery_task_ids"]) == 3
    assert mock_celery_task.call_count == 3
