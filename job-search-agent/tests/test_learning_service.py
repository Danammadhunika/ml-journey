"""
tests/test_learning_service.py
--------------------------------
Tests for the Daily Learning Log (database/learning_service.py).

Uses a fresh in-memory SQLite database per test, same pattern as
tests/test_tracker.py.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base
from database.learning_service import (
    LearningError,
    get_learning_entry,
    list_learning,
    log_learning,
    set_learning_status,
)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def test_log_learning_creates_entry_with_learning_status(session):
    entry = log_learning(session, "Python")
    session.commit()

    assert entry.skill == "Python"
    assert entry.status == "LEARNING"
    assert entry.mention_count == 1
    assert entry.added_to_resume is False


def test_log_learning_twice_same_skill_increments_mention_count_not_duplicate(session):
    log_learning(session, "SQL")
    session.commit()
    second = log_learning(session, "sql", note="practiced joins")
    session.commit()

    assert second.mention_count == 2
    assert "practiced joins" in second.notes

    all_entries = list_learning(session)
    assert len(all_entries) == 1  # no duplicate row for a second mention


def test_set_learning_status_moves_skill_forward(session):
    log_learning(session, "FastAPI")
    session.commit()

    updated = set_learning_status(session, "FastAPI", "CONFIDENT", mark_added_to_resume=True)
    session.commit()

    assert updated.status == "CONFIDENT"
    assert updated.added_to_resume is True


def test_set_learning_status_rejects_unknown_status(session):
    log_learning(session, "Docker")
    session.commit()
    with pytest.raises(LearningError):
        set_learning_status(session, "Docker", "EXPERT")


def test_get_learning_entry_unknown_skill_raises(session):
    with pytest.raises(LearningError):
        get_learning_entry(session, "Rust")


def test_list_learning_filters_by_status(session):
    log_learning(session, "Python")
    log_learning(session, "Kubernetes")
    session.commit()
    set_learning_status(session, "Python", "CONFIDENT")
    session.commit()

    confident_only = list_learning(session, status="CONFIDENT")
    assert [e.skill for e in confident_only] == ["Python"]
