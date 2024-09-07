import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filman_server.database import models, schemas
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


# Guild configuration process
# /discord/configure/guild
def test_configure_guild(test_client):
    test_guilds_data = [
        {"discord_guild_id": 1209989703772799056, "discord_channel_id": 132632676225122304},
        {"discord_guild_id": 1209989703772799056, "discord_channel_id": 132632676225122305},
        {"discord_guild_id": 1209989703772799057, "discord_channel_id": 132632676225122306},
    ]

    for guild_data in test_guilds_data:
        response = test_client.post("/discord/configure/guild", json=guild_data)
        assert response.status_code == 200

        guild = response.json()

        assert guild["id"] > 0
        assert guild["discord_guild_id"] == guild_data["discord_guild_id"]
        assert guild["discord_channel_id"] == guild_data["discord_channel_id"]
