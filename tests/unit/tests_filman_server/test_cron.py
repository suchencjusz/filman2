from unittest.mock import patch

import pytest
import requests

from filman_server.cron import Cron


@pytest.fixture
def cron():
    return Cron()


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_users_series(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_users_series()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/series", timeout=10
    )


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_series(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_series()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/new/scrap/filmweb/series", timeout=10
    )


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_users_movies(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_users_movies()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/movies", timeout=10
    )


@patch("filman_server.cron.requests.get")
def test_tasks_new_scrap_filmweb_movies(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_new_scrap_filmweb_movies()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/new/scrap/filmweb/movies", timeout=10
    )


@patch("filman_server.cron.requests.get")
def test_tasks_update_stuck_tasks(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_update_stuck_tasks()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/update/stuck/5", timeout=10
    )


@patch("filman_server.cron.requests.get")
def test_tasks_update_old_tasks(mock_get):
    mock_get.return_value.status_code = 200
    Cron.tasks_update_old_tasks()
    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/update/old/20", timeout=10
    )


# test exceptions execute_task
@patch("filman_server.cron.requests.get")
@patch("filman_server.cron.logging.info")
def test_execute_task_success(mock_logging_info, mock_get):
    mock_get.return_value.status_code = 200

    Cron.execute_task(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/series", "test_task"
    )

    mock_get.assert_called_once_with(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/series", timeout=10
    )
    mock_logging_info.assert_called_once_with("Executed test_task: 200")


@patch("filman_server.cron.requests.get", side_effect=requests.exceptions.Timeout)
@patch("filman_server.cron.logging.error")
def test_execute_task_timeout(mock_logging_error, mock_get):
    Cron.execute_task(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/series", "test_task"
    )

    mock_logging_error.assert_called_once_with(
        "Timeout occurred while executing test_task"
    )


@patch(
    "filman_server.cron.requests.get",
    side_effect=requests.exceptions.RequestException("Connection error"),
)
@patch("filman_server.cron.logging.error")
def test_execute_task_exception(mock_logging_error, mock_get):
    Cron.execute_task(
        "http://localhost:8000/tasks/new/scrap/filmweb/users/series", "test_task"
    )

    mock_logging_error.assert_called_once_with(
        "An error occurred while executing test_task: Connection error"
    )


# test start function
@patch("filman_server.cron.Thread")
def test_start(mock_thread, cron):
    cron.start()
    assert mock_thread.called
    assert mock_thread.return_value.start.called
