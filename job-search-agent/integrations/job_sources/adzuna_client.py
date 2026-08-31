"""
integrations/job_sources/adzuna_client.py
---------------------------------------------
A small, read-only client for the Adzuna job search API.

WHY ADZUNA, AND NOT INDEED/DICE/GLASSDOOR/JOBRIGHT DIRECTLY:
Those sites don't offer a general-purpose public API for this kind of use,
and their Terms of Service prohibit scraping -- doing that would break
this project's own hard rule (never bypass ToS/rate limits) and put your
accounts at real risk of being banned. Adzuna, by contrast, is a job
aggregator (it pulls listings from many sources, including some of those
same sites) that explicitly publishes a free, public search API meant for
exactly this kind of use -- no scraping, no ToS violation, no account risk.

Sign up for a free app_id/app_key at https://developer.adzuna.com/ and put
them in your .env as ADZUNA_APP_ID / ADZUNA_APP_KEY.
"""

from __future__ import annotations

import httpx

from config.logging_setup import get_logger
from config.settings import settings

logger = get_logger(__name__)

_API_BASE = "https://api.adzuna.com/v1/api/jobs"


class JobBoardError(Exception):
    """Raised for any problem talking to the job search API (missing
    credentials, network error, no results, etc.) -- always a clear,
    specific message."""


def search_jobs(
    query: str,
    location: str = "",
    results_per_page: int = 10,
    page: int = 1,
) -> list[dict]:
    """
    Real, live job postings matching `query` (and optionally `location`),
    straight from Adzuna's public API. Each result is a plain dict with
    at least: title, company, location, description, redirect_url,
    created (date), and salary_min/salary_max when Adzuna has them.

    Raises JobBoardError if ADZUNA_APP_ID/ADZUNA_APP_KEY aren't set, or if
    the request fails.
    """
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise JobBoardError(
            "No Adzuna API credentials found. Sign up for a free account at "
            "https://developer.adzuna.com/ and set ADZUNA_APP_ID and "
            "ADZUNA_APP_KEY in your .env."
        )

    url = f"{_API_BASE}/{settings.adzuna_country}/search/{page}"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    try:
        response = httpx.get(url, params=params, timeout=20.0)
    except httpx.RequestError as e:
        raise JobBoardError(f"Could not reach Adzuna: {e}") from e

    if response.status_code == 401:
        raise JobBoardError(
            "Adzuna rejected your app_id/app_key. Double-check ADZUNA_APP_ID "
            "and ADZUNA_APP_KEY in your .env."
        )
    if response.status_code >= 400:
        raise JobBoardError(
            f"Adzuna returned {response.status_code}: {response.text[:200]}"
        )

    data = response.json()
    results = data.get("results", [])

    jobs: list[dict] = []
    for r in results:
        jobs.append(
            {
                "title": r.get("title", ""),
                "company": (r.get("company") or {}).get("display_name", ""),
                "location": (r.get("location") or {}).get("display_name", ""),
                "description": r.get("description", ""),
                "redirect_url": r.get("redirect_url", ""),
                "created": r.get("created", ""),
                "salary_min": r.get("salary_min"),
                "salary_max": r.get("salary_max"),
            }
        )
    return jobs
