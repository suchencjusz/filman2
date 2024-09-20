from unittest.mock import patch

import pytest

from filman_server.cron import Cron


@pytest.fixture
def cron():
    return Cron()


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_users_movies(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_users_movies()
    mock_get.assert_called_once_with("http://localhost:8000/tasks/new/scrap/filmweb/users/movies", timeout=5)


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_movies(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_movies()
    mock_get.assert_called_once_with("http://localhost:8000/tasks/new/scrap/filmweb/movies", timeout=5)


@patch("filman_server.cron.requests.get")
def test_tasks_update_stuck_tasks(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_update_stuck_tasks()
    mock_get.assert_called_once_with("http://localhost:8000/tasks/update/stuck/5", timeout=5)


@patch("filman_server.cron.requests.get")
def test_tasks_update_old_tasks(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_update_old_tasks()
    mock_get.assert_called_once_with("http://localhost:8000/tasks/update/old/20", timeout=5)


@patch("filman_server.cron.Thread")
def test_start(mock_thread, cron):
    cron.start()
    assert mock_thread.called
    assert mock_thread.return_value.start.called
