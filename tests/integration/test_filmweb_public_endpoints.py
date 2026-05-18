from __future__ import annotations

from pathlib import Path

import pytest
import requests


MOVIE_ID = "734"
SERIES_ID = "697645"
FILMWEB_USER_ID = "sucheta348"
FILMWEB_USER_NUMERIC_ID = "4347201"
MOVIE_TITLE_SLUG = "placeholder-title"
MOVIE_YEAR = "2024"


def _extract_url_templates(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    return [line.strip() for line in content.splitlines() if line.strip().startswith("https://www.filmweb.pl/")]


def _base_replace(template: str) -> str:
    return (
        template.replace("{filmweb_id}", FILMWEB_USER_ID)
        .replace("{filmweb_user_id}", FILMWEB_USER_NUMERIC_ID)
        .replace("{movie_id}", MOVIE_ID)
        .replace("{series_id}", SERIES_ID)
        .replace("{title}", MOVIE_TITLE_SLUG)
        .replace("{year}", MOVIE_YEAR)
    )


def _expand_template(template: str) -> list[str]:
    template = _base_replace(template)

    if "{film|serial}" in template:
        film_url = template.replace("{film|serial}", "film")
        serial_url = template.replace("{film|serial}", "serial")
        return [film_url.replace("{id}", MOVIE_ID), serial_url.replace("{id}", SERIES_ID)]

    if "{id}" in template:
        if "/api/v1/title/" in template or "/api/v1/film/" in template:
            return [template.replace("{id}", MOVIE_ID), template.replace("{id}", SERIES_ID)]
        return [template.replace("{id}", MOVIE_ID)]

    return [template]


def _build_urls() -> list[str]:
    templates = _extract_url_templates(Path("readme/filmweb_endpoints.txt"))
    urls: list[str] = []

    for template in templates:
        urls.extend(_expand_template(template))

    # Keep insertion order while deduplicating.
    return list(dict.fromkeys(urls))


def _assert_preview_payload(payload: dict[str, object]) -> None:
    expected_keys = {
        "directors",
        "year",
        "entityName",
        "subType",
        "description",
        "poster",
        "genres",
        "countries",
        "duration",
        "plotOrDescriptionSynopsis",
    }
    missing = [key for key in expected_keys if key not in payload]
    assert not missing, f"Missing preview keys: {missing}"


def _assert_votes_payload(payload: dict[str, object]) -> None:
    votes = payload.get("votes")
    assert isinstance(votes, list), "Expected 'votes' list in response"
    if not votes:
        return

    first = votes[0]
    assert isinstance(first, dict), "Expected votes entries to be objects"
    assert "id" in first and "timestamp" in first, "Vote entry missing id or timestamp"

    vote_id = first.get("id")
    assert isinstance(vote_id, dict), "Expected vote.id to be an object"
    assert "id" in vote_id and "name" in vote_id, "Vote id missing id/name"


def _assert_rating_payload(payload: dict[str, object]) -> None:
    expected_keys = {
        "count",
        "rate",
        "countWantToSee",
        "countVote1",
        "countVote2",
        "countVote3",
        "countVote4",
        "countVote5",
        "countVote6",
        "countVote7",
        "countVote8",
        "countVote9",
        "countVote10",
    }
    missing = [key for key in expected_keys if key not in payload]
    assert not missing, f"Missing rating keys: {missing}"


@pytest.mark.parametrize("url", _build_urls())
def test_filmweb_endpoint_reachable(url: str):

    # czy te endpoint wgl istnieja

    response = requests.get(url, timeout=10, allow_redirects=True)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code} for {url}"

    if url == "https://www.filmweb.pl/api/v1/film/10119673/preview":
        _assert_preview_payload(response.json())

    if url == "https://www.filmweb.pl/api/v1/users/4347201/votes/film":
        _assert_votes_payload(response.json())

    if url.endswith("/rating") and "/api/v1/film/" in url and "/critics/" not in url:
        _assert_rating_payload(response.json())
