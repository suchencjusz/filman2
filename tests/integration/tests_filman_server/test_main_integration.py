import pytest
from fastapi.testclient import TestClient

from filman_server.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_sentry_debug():
    with pytest.raises(ZeroDivisionError):
        client.get("/sentry-debug")
