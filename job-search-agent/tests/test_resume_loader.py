"""
tests/test_resume_loader.py
----------------------------
Tests for resume/loader.py and resume/schema.py.

WHY THIS FILE EXISTS:
Since this whole project depends on the master resume being read
correctly, we want an automated check that:
  1. A valid resume file loads without errors.
  2. An invalid/missing-field resume file is REJECTED with a clear error
     (not silently accepted with wrong data).

Run with:  pytest
"""

import json

import pytest
from pydantic import ValidationError

from resume.loader import (
    ResumeNotFoundError,
    ResumeValidationError,
    load_master_resume,
)
from resume.schema import MasterResume

VALID_RESUME = {
    "contact": {
        "name": "Test Person",
        "email": "test@example.com",
        "location": "United States",
    },
    "summary": "A short professional summary for testing.",
    "skills": ["Python", "FastAPI", "AWS"],
    "experience": [
        {
            "company": "Test Co",
            "title": "Software Engineer",
            "start_date": "Jan 2023",
            "end_date": "Present",
            "bullets": ["Built and shipped a REST API used by internal teams."],
        }
    ],
    "education": [
        {
            "institution": "Test University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science",
        }
    ],
}


def test_valid_resume_parses_into_master_resume():
    """A well-formed dict should turn into a MasterResume object."""
    resume = MasterResume.model_validate(VALID_RESUME)
    assert resume.contact.name == "Test Person"
    assert "python" in resume.all_skill_terms()


def test_missing_required_field_raises_validation_error():
    """Dropping a required field (contact.email) should fail validation,
    not silently succeed with a blank email."""
    broken = json.loads(json.dumps(VALID_RESUME))  # deep copy
    del broken["contact"]["email"]
    with pytest.raises(ValidationError):
        MasterResume.model_validate(broken)


def test_load_master_resume_missing_file_raises_friendly_error(tmp_path):
    """If master_resume.json doesn't exist yet, we should get our custom
    ResumeNotFoundError (with instructions), not a raw FileNotFoundError."""
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(ResumeNotFoundError):
        load_master_resume(path=missing_path)


def test_load_master_resume_invalid_json_raises_friendly_error(tmp_path):
    """If the file exists but isn't valid JSON, we should get our custom
    ResumeValidationError with a helpful message."""
    bad_file = tmp_path / "master_resume.json"
    bad_file.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ResumeValidationError):
        load_master_resume(path=bad_file)


def test_load_master_resume_valid_file_loads(tmp_path):
    """End-to-end: write a valid resume to disk and load it back."""
    good_file = tmp_path / "master_resume.json"
    good_file.write_text(json.dumps(VALID_RESUME), encoding="utf-8")
    resume = load_master_resume(path=good_file)
    assert resume.contact.name == "Test Person"
