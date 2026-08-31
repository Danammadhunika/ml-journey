"""
integrations/github/client.py
--------------------------------
A small, read-only client for GitHub's public REST API. Used by the
Project Importer to pull real facts about your own repositories (name,
description, languages, topics, README text) -- nothing here ever writes
to GitHub; it only reads what's already public.

WHY A PLAIN REQUESTS WRAPPER INSTEAD OF A GITHUB SDK:
We only need three read-only endpoints. A full SDK would be a heavier
dependency for very little benefit -- `httpx` (already a dependency here)
is all we need.
"""

from __future__ import annotations

import base64

import httpx

from config.logging_setup import get_logger
from config.settings import settings

logger = get_logger(__name__)

_API_BASE = "https://api.github.com"


class GitHubError(Exception):
    """Raised for any problem talking to GitHub (repo not found, rate
    limited, network error, etc.) -- always a clear, specific message."""


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _get(path: str) -> httpx.Response:
    url = f"{_API_BASE}{path}"
    try:
        response = httpx.get(url, headers=_headers(), timeout=20.0)
    except httpx.RequestError as e:
        raise GitHubError(f"Could not reach GitHub: {e}") from e

    if response.status_code == 404:
        raise GitHubError(f"GitHub returned 'not found' for {url}")
    if response.status_code == 403 and "rate limit" in response.text.lower():
        raise GitHubError(
            "GitHub rate limit hit. Unauthenticated requests are limited to "
            "60/hour -- set GITHUB_TOKEN in your .env (a public_repo-read "
            "token) to raise that to 5000/hour."
        )
    if response.status_code >= 400:
        raise GitHubError(f"GitHub returned {response.status_code} for {url}: {response.text[:200]}")
    return response


class RepoSummary(dict):
    """A lightweight repo listing entry -- kept as a plain dict (not a
    Pydantic model) since this is raw external data we pass straight
    through, not something we validate our own schema against."""


def list_public_repos(username: str) -> list[dict]:
    """All of a user's public, non-fork repositories, newest-pushed first."""
    response = _get(f"/users/{username}/repos?type=owner&sort=pushed&per_page=100")
    repos = response.json()
    return [r for r in repos if not r.get("fork")]


def get_repo(username: str, repo_name: str) -> dict:
    """Full details for one repo (description, language, topics, etc.)."""
    response = _get(f"/repos/{username}/{repo_name}")
    return response.json()


def get_readme_text(username: str, repo_name: str) -> str | None:
    """
    The repo's README, decoded to plain text. Returns None (not an error)
    if the repo simply doesn't have one -- that's normal, not a failure.
    """
    try:
        response = _get(f"/repos/{username}/{repo_name}/readme")
    except GitHubError as e:
        if "not found" in str(e).lower():
            return None
        raise

    data = response.json()
    content = data.get("content", "")
    try:
        return base64.b64decode(content).decode("utf-8", errors="replace")
    except Exception as e:  # pragma: no cover - decoding a real README essentially never fails
        logger.warning("Could not decode README for %s/%s: %s", username, repo_name, e)
        return None
