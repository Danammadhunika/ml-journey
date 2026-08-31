"""
resume/experience_utils.py
----------------------------
Deterministic (non-LLM) helpers for reasoning about your work history.

WHY THIS IS PYTHON, NOT THE LLM:
"How many years of experience does this resume represent?" is basic
arithmetic on dates you already typed in — there's no judgment call for an
LLM to make, and asking an LLM to count months reliably is exactly the
kind of thing language models are bad at. Keeping it in plain Python means
the number is 100% reproducible and testable.
"""

import re
from datetime import date

from resume.schema import MasterResume

_MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_PRESENT_WORDS = {"present", "current", "now", "ongoing"}


def parse_month_year(text: str, *, today: date | None = None) -> date | None:
    """
    Parse free-text dates like "Jan 2026", "January 2026", "2026", or
    "Present" into a `date` (day is always set to 1 — we only ever care
    about month/year precision for duration math).

    Returns None if the text can't be parsed (so callers can decide to
    skip that entry rather than guess).
    """
    today = today or date.today()
    cleaned = text.strip().lower()

    if cleaned in _PRESENT_WORDS:
        return today

    match = re.match(r"([a-zA-Z]+)\s+(\d{4})", cleaned)
    if match:
        month_name, year_str = match.groups()
        month = _MONTHS.get(month_name[:3]) or _MONTHS.get(month_name)
        if month:
            return date(int(year_str), month, 1)

    match = re.match(r"^(\d{4})$", cleaned)
    if match:
        return date(int(match.group(1)), 1, 1)

    return None


def parse_total_experience_years(resume: MasterResume, *, today: date | None = None) -> float:
    """
    Sum the duration of every experience entry into total years.

    Simplification (documented, not hidden): overlapping roles are added
    together rather than de-duplicated by calendar time. For most resumes
    (sequential jobs) this matches reality; if you ever hold two jobs at
    once, this will over-count — worth revisiting before relying on it for
    that case.
    """
    today = today or date.today()
    total_months = 0

    for entry in resume.experience:
        start = parse_month_year(entry.start_date, today=today)
        end = parse_month_year(entry.end_date, today=today)
        if start is None or end is None or end < start:
            continue  # unparseable or nonsensical — skip rather than guess
        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += max(months, 0)

    return round(total_months / 12, 1)
