import datetime
from unittest.mock import MagicMock

import requests

from filman_crawler.main import check_there_are_any_tasks, do_task, get_task_to_do
from filman_crawler.tasks.scrap_movie import Scraper as MovieScraper
from filman_crawler.tasks.utils import DEFAULT_TIMEOUT, SERVER_HEADERS, Tasks
from filman_server.database.schemas import Task, TaskStatus, TaskTypes


def test_tasks_client_uses_timeout_and_server_headers():
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock(status_code=200)
    mock_session.request.return_value = mock_response

    tasks_client = Tasks(
        headers={"Host": "www.filmweb.pl", "User-Agent": "ua"},
        endpoint_url="http://filman_server:8000",
        session=mock_session,
    )

    assert tasks_client.update_task_status(42, TaskStatus.COMPLETED) is True
    mock_session.request.assert_called_once_with(
        "GET",
        "http://filman_server:8000/tasks/update/status/42/completed",
        timeout=DEFAULT_TIMEOUT,
        headers=SERVER_HEADERS,
    )


def test_tasks_client_handles_request_exception():
    mock_session = MagicMock(spec=requests.Session)
    mock_session.request.side_effect = requests.exceptions.Timeout("timed out")

    tasks_client = Tasks(
        headers={"Host": "www.filmweb.pl"},
        endpoint_url="http://filman_server:8000",
        session=mock_session,
    )

    assert tasks_client.update_task_status(42, TaskStatus.ERROR) is False


def test_check_there_are_any_tasks_passes_timeout(monkeypatch):
    mock_session = MagicMock(spec=requests.Session)
    mock_session.head.return_value = MagicMock(status_code=200)
    monkeypatch.setattr("filman_crawler.main._server_session", mock_session)

    assert check_there_are_any_tasks() is True
    assert mock_session.head.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT
    assert mock_session.head.call_args.kwargs["headers"] == SERVER_HEADERS


def test_get_task_to_do_handles_404_and_connection_error(monkeypatch):
    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.return_value = MagicMock(status_code=404)
    monkeypatch.setattr("filman_crawler.main._server_session", mock_session)

    task, reachable = get_task_to_do()
    assert task is None
    assert reachable is True

    mock_session.get.side_effect = requests.exceptions.ConnectionError("refused")
    task, reachable = get_task_to_do()
    assert task is None
    assert reachable is False


def test_do_task_marks_error_when_scraper_raises(monkeypatch):
    mock_tasks_instance = MagicMock()
    monkeypatch.setattr("filman_crawler.main.Tasks", MagicMock(return_value=mock_tasks_instance))

    mock_scraper = MagicMock()
    mock_scraper.scrap.side_effect = RuntimeError("boom")
    monkeypatch.setattr("filman_crawler.main.movie_scrapper", MagicMock(return_value=mock_scraper))

    task = Task(
        task_id=7,
        task_status=TaskStatus.RUNNING,
        task_type=TaskTypes.SCRAP_FILMWEB_MOVIE,
        task_job="628",
        task_created=datetime.datetime.now(),
    )

    do_task(task)
    mock_tasks_instance.update_task_status.assert_called_once_with(7, TaskStatus.ERROR)


def test_movie_scraper_returns_false_on_invalid_json(monkeypatch):
    scraper = MovieScraper(headers={}, endpoint_url="http://filman_server:8000", movie_id="628")
    monkeypatch.setattr(scraper, "fetch", lambda url: "not-json")

    task = Task(
        task_id=1,
        task_status=TaskStatus.RUNNING,
        task_type=TaskTypes.SCRAP_FILMWEB_MOVIE,
        task_job="628",
        task_created=datetime.datetime.now(),
    )

    assert scraper.scrap(task) is False
