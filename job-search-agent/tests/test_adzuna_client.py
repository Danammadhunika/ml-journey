"""
tests/test_adzuna_client.py
-------------------------------
Tests for integrations/job_sources/adzuna_client.py.

No real network calls: `httpx.get` is mocked out so these run offline.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from config.settings import settings
from integrations.job_sources.adzuna_client import JobBoardError, search_jobs


def _fake_response(status_code: int, json_data=None, text: str = ""):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = text
    return response


def test_search_jobs_raises_without_credentials(monkeypatch):
    monkeypatch.setattr(settings, "adzuna_app_id", "")
    monkeypatch.setattr(settings, "adzuna_app_key", "")
    with pytest.raises(JobBoardError, match="credentials"):
        search_jobs("python developer")


def test_search_jobs_returns_parsed_results(monkeypatch):
    monkeypatch.setattr(settings, "adzuna_app_id", "fake-id")
    monkeypatch.setattr(settings, "adzuna_app_key", "fake-key")
    fake_payload = {
        "results": [
            {
                "title": "Python Developer",
                "company": {"display_name": "Acme Corp"},
                "location": {"display_name": "Remote"},
                "description": "Build things with Python.",
                "redirect_url": "https://example.com/job/1",
                "created": "2026-08-01T00:00:00Z",
                "salary_min": 90000,
                "salary_max": 120000,
            }
        ]
    }
    with patch("integrations.job_sources.adzuna_client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(200, fake_payload)
        jobs = search_jobs("python developer", location="remote")

    assert len(jobs) == 1
    assert jobs[0]["title"] == "Python Developer"
    assert jobs[0]["company"] == "Acme Corp"
    assert jobs[0]["salary_min"] == 90000


def test_search_jobs_raises_on_bad_credentials(monkeypatch):
    monkeypatch.setattr(settings, "adzuna_app_id", "fake-id")
    monkeypatch.setattr(settings, "adzuna_app_key", "fake-key")
    with patch("integrations.job_sources.adzuna_client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(401, text="Unauthorized")
        with pytest.raises(JobBoardError, match="rejected"):
            search_jobs("python developer")


def test_search_jobs_handles_missing_optional_fields(monkeypatch):
    monkeypatch.setattr(settings, "adzuna_app_id", "fake-id")
    monkeypatch.setattr(settings, "adzuna_app_key", "fake-key")
    fake_payload = {"results": [{"title": "Data Analyst"}]}
    with patch("integrations.job_sources.adzuna_client.httpx.get") as mock_get:
        mock_get.return_value = _fake_response(200, fake_payload)
        jobs = search_jobs("data analyst")

    assert jobs[0]["title"] == "Data Analyst"
    assert jobs[0]["company"] == ""
    assert jobs[0]["salary_min"] is None
