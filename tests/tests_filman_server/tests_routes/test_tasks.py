import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filman_server.main import app
from filman_server.database import models
from filman_server.database.db import Base, get_db

# Create an in-memory SQLite database engine for testing
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


# Nomral task creation process
def test_create_task(test_client):
    task_data = {
        "task_status": "queued",
        "task_type": "scrap_user",
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
def test_tasks_to_do_head(test_client):
    task_data_list = [
        {
            "task_status": "queued",
            "task_type": "scrap_user",
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
        (["scrap_user"], 200),
        (["scrap_filmweb_movie"], 200),
        (["scrap_filmweb_user_watched_series"], 200),
        (["scrap_filmweb_user_watched_series", "scrap_filmweb_movie"], 200),
        (["scrap_user", "scrap_filmweb_movie", "scrap_filmweb_user_watched_series"], 200),
        (["scrap_user", "scrap_filmweb_movie", "scrap_filmweb_user_watched_series", "scrap_filmweb_series"], 200),
        ([], 422),
        ([""], 422),
        (["hello"], 422),
        (["scrap_filmweb_user_watched_movies"], 404),
        (["scrap_filmweb_series", "scrap_filmweb_user_watched_movies"], 404),
    ]

    # Perform assertions
    for task_types, expected_status in task_types_and_status_codes:
        response = test_client.head("/tasks/get/task/to_do", params={"task_types": task_types})
        assert response.status_code == expected_status
