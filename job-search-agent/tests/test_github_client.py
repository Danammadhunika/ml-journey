"""
tests/test_github_client.py
-------------------------------
Tests for integrations/github/client.py.

No real network calls: `httpx.get` is mocked out so these run offline
and don't count against GitHub's rate limit.
"""

import base64
from unittest.mock import MagicMock, patch

import httpx
import pytest

from integrations.github.client import GitHubError, get_readme_text, get_repo, list_public_repos


def _fake_response(status_code: int, json_data=None, text: str = ""):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = text
    return response


def test_get_repo_returns_json_on_success():
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(200, {"name": "movie-rec-app", "language": "Python"})
        repo = get_repo("testuser", "movie-rec-app")
    assert repo["name"] == "movie-rec-app"


def test_get_repo_not_found_raises_github_error():
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(404, text="Not Found")
        with pytest.raises(GitHubError):
            get_repo("testuser", "does-not-exist")


def test_rate_limit_error_has_helpful_message():
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(403, text="API rate limit exceeded")
        with pytest.raises(GitHubError, match="rate limit"):
            get_repo("testuser", "movie-rec-app")


def test_list_public_repos_filters_out_forks():
    repos = [
        {"name": "own-project", "fork": False},
        {"name": "forked-project", "fork": True},
    ]
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(200, repos)
        result = list_public_repos("testuser")
    assert [r["name"] for r in result] == ["own-project"]


def test_get_readme_text_decodes_base64_content():
    readme_content = "# Hello\nThis is a README."
    encoded = base64.b64encode(readme_content.encode("utf-8")).decode("ascii")
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(200, {"content": encoded})
        text = get_readme_text("testuser", "movie-rec-app")
    assert text == readme_content


def test_get_readme_text_returns_none_when_repo_has_no_readme():
    with patch("integrations.github.client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(404, text="Not Found")
        text = get_readme_text("testuser", "movie-rec-app")
    assert text is None
