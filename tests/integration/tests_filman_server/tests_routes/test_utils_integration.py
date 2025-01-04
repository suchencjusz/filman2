import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filman_server.database.db import Base, get_db
from filman_server.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)


def test_get_database_info(test_client):
    response = test_client.get("/utils/database_info")
    assert response.status_code == 200
    data = response.json()
    assert "users_count" in data
    assert "filmweb_watched_movies" in data
    assert "filmweb_watched_series" in data
    assert "discord_guilds" in data
