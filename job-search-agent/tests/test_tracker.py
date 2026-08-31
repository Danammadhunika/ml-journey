"""
tests/test_tracker.py
----------------------
Tests for the Application Tracker (database/tracker_service.py).

These use a fresh in-memory SQLite database per test (not your real
database/job_search.db), so running the test suite never touches or
pollutes your actual tracked applications.
"""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.job_matcher import LLMJobAnalysis, MatchResult
from database.models import Base
from database.tracker_service import (
    TrackerError,
    find_latest_by_company,
    get_application,
    list_applications,
    log_company_update,
    save_match_result,
    update_status,
)


@pytest.fixture()
def session():
    """A clean in-memory database, torn down automatically after each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def make_match_result(**overrides) -> MatchResult:
    defaults = dict(
        overall_score=85,
        technical_skills_score=90,
        experience_score=100,
        education_score=100,
        seniority_score=80,
        location_score=100,
        sponsorship_compatibility="UNKNOWN",
        sponsorship_note=None,
        strengths=["Strong Python background."],
        gaps=["No direct AWS experience."],
        missing_requirements=["AWS certification preferred"],
        recommendation="APPLY",
        reason="Good overall fit.",
        llm_analysis=LLMJobAnalysis(summary_reason="Good overall fit."),
    )
    defaults.update(overrides)
    return MatchResult(**defaults)


def test_save_match_result_creates_row_with_not_applied_status(session):
    result = make_match_result()
    application = save_match_result(
        session,
        job_title="Data Analyst",
        job_description_text="Some JD text.",
        match_result=result,
        company="Acme Corp",
        source_url="https://example.com/job/123",
    )
    session.commit()

    assert application.id is not None
    assert application.status == "NOT_APPLIED"
    assert application.company == "Acme Corp"
    assert application.overall_score == 85
    assert json.loads(application.strengths_json) == ["Strong Python background."]


def test_save_match_result_twice_creates_two_rows(session):
    result = make_match_result()
    save_match_result(
        session, job_title="Data Analyst", job_description_text="JD 1", match_result=result
    )
    save_match_result(
        session, job_title="Data Analyst", job_description_text="JD 2 (re-scored)", match_result=result
    )
    session.commit()

    all_apps = list_applications(session)
    assert len(all_apps) == 2


def test_list_applications_orders_newest_first(session):
    result = make_match_result()
    first = save_match_result(
        session, job_title="First Job", job_description_text="JD", match_result=result
    )
    second = save_match_result(
        session, job_title="Second Job", job_description_text="JD", match_result=result
    )
    session.commit()

    all_apps = list_applications(session)
    assert [a.id for a in all_apps] == [second.id, first.id]


def test_list_applications_filters_by_status(session):
    result = make_match_result()
    applied = save_match_result(
        session, job_title="Applied Job", job_description_text="JD", match_result=result
    )
    save_match_result(
        session, job_title="Not Applied Job", job_description_text="JD", match_result=result
    )
    session.commit()
    update_status(session, applied.id, "APPLIED")
    session.commit()

    applied_only = list_applications(session, status="APPLIED")
    assert [a.id for a in applied_only] == [applied.id]


def test_list_applications_rejects_unknown_status(session):
    with pytest.raises(TrackerError):
        list_applications(session, status="GHOSTED")  # not a real status


def test_update_status_sets_timestamp_and_notes(session):
    result = make_match_result()
    application = save_match_result(
        session, job_title="Data Analyst", job_description_text="JD", match_result=result
    )
    session.commit()

    updated = update_status(session, application.id, "APPLIED", notes="Applied via referral.")
    session.commit()

    assert updated.status == "APPLIED"
    assert updated.status_updated_at is not None
    assert updated.notes == "Applied via referral."


def test_update_status_rejects_unknown_status(session):
    result = make_match_result()
    application = save_match_result(
        session, job_title="Data Analyst", job_description_text="JD", match_result=result
    )
    session.commit()

    with pytest.raises(TrackerError):
        update_status(session, application.id, "GHOSTED")


def test_update_status_unknown_id_raises(session):
    with pytest.raises(TrackerError):
        update_status(session, 999, "APPLIED")


def test_get_application_unknown_id_raises(session):
    with pytest.raises(TrackerError):
        get_application(session, 999)


# ---------------------------------------------------------------------------
# Company-based dedup logging (log_company_update / find_latest_by_company)
# -- added 2026-08-31 for the "don't create a duplicate every time a
# company is mentioned again" requirement.
# ---------------------------------------------------------------------------


def test_log_company_update_creates_new_row_for_unknown_company(session):
    application, created = log_company_update(
        session, "HCL", status="RECRUITER_SCREENING", notes="Screening completed."
    )
    session.commit()

    assert created is True
    assert application.company == "HCL"
    assert application.status == "RECRUITER_SCREENING"
    assert application.notes == "Screening completed."
    # Placeholder score fields, since this wasn't scored via match-job:
    assert application.overall_score == 0
    assert application.job_description_text.startswith("(logged directly")


def test_log_company_update_updates_existing_row_case_insensitively(session):
    first, created = log_company_update(session, "HCL", status="RECRUITER_SCREENING")
    session.commit()

    second, created_again = log_company_update(
        session, "hcl", status="RESUME_SUBMITTED", interview_notes="Expected soon"
    )
    session.commit()

    assert created is True
    assert created_again is False
    assert second.id == first.id
    assert second.status == "RESUME_SUBMITTED"
    assert second.interview_notes == "Expected soon"

    all_apps = list_applications(session)
    assert len(all_apps) == 1  # no duplicate row was created


def test_log_company_update_only_touches_fields_that_were_passed(session):
    log_company_update(session, "Deloitte", status="RECRUITER_SCREENING", notes="Initial note")
    session.commit()

    updated, _ = log_company_update(session, "Deloitte", interview_notes="Scheduled for Sep 5")
    session.commit()

    # notes and status from the first call must survive an update that
    # didn't mention them at all.
    assert updated.notes == "Initial note"
    assert updated.status == "RECRUITER_SCREENING"
    assert updated.interview_notes == "Scheduled for Sep 5"


def test_log_company_update_rejects_unknown_status(session):
    with pytest.raises(TrackerError):
        log_company_update(session, "Meta", status="GHOSTED")


def test_find_latest_by_company_returns_none_when_untracked(session):
    assert find_latest_by_company(session, "Nonexistent Co") is None


def test_find_latest_by_company_returns_most_recent(session):
    result = make_match_result()
    save_match_result(
        session, job_title="Old Role", job_description_text="JD", match_result=result, company="Acme"
    )
    session.commit()
    newer = save_match_result(
        session, job_title="New Role", job_description_text="JD 2", match_result=result, company="Acme"
    )
    session.commit()

    found = find_latest_by_company(session, "acme")
    assert found.id == newer.id
