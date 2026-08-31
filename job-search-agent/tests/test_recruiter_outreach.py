"""
tests/test_recruiter_outreach.py
------------------------------------
Tests for the Recruiter Outreach Agent.

Same split as the other agent test files:
  1. `verify_claims` -- pure Python, no LLM. This is the important one:
     it's the safety net that flags anything the LLM claims that isn't
     actually backed by the resume.
  2. One end-to-end test of `RecruiterOutreachAgent.draft()` with a fake
     LLM provider (no real API calls).
"""

from agents.recruiter_outreach import (
    LLMOutreachDraft,
    RecruiterOutreachAgent,
    verify_claims,
)
from integrations.llm.base import LLMProvider
from resume.schema import ContactInfo, Education, Experience, MasterResume


def make_resume(**overrides) -> MasterResume:
    defaults = dict(
        contact=ContactInfo(name="Test Person", email="test@example.com"),
        summary="A test summary about Python and SQL work.",
        skills=["Python", "SQL", "AWS"],
        experience=[
            Experience(
                company="Acme Analytics",
                client="Globex Corp",
                title="Data Analyst",
                start_date="Jan 2023",
                end_date="Present",
                bullets=["Built dashboards using Matplotlib and Seaborn."],
            )
        ],
        education=[
            Education(
                institution="Test University",
                degree="M.S.",
                field_of_study="Computer Science",
                gpa="3.9/4.0",
            )
        ],
    )
    defaults.update(overrides)
    return MasterResume(**defaults)


# ---------------------------------------------------------------------------
# verify_claims
# ---------------------------------------------------------------------------


def test_verify_claims_accepts_true_facts():
    resume = make_resume()
    verified, unverified = verify_claims(
        ["Python", "SQL", "Acme Analytics", "Test University"], resume
    )
    assert verified == ["Python", "SQL", "Acme Analytics", "Test University"]
    assert unverified == []


def test_verify_claims_flags_fabricated_fact():
    resume = make_resume()
    verified, unverified = verify_claims(["Kubernetes", "Python"], resume)
    assert "Python" in verified
    assert "Kubernetes" in unverified


def test_verify_claims_accepts_near_verbatim_metric():
    resume = make_resume()
    verified, unverified = verify_claims(["3.9/4.0 GPA"], resume)
    assert verified == ["3.9/4.0 GPA"]
    assert unverified == []


def test_verify_claims_flags_fabricated_metric():
    resume = make_resume()
    # Resume has no such number anywhere -- should not verify.
    verified, unverified = verify_claims(["500000 rows processed"], resume)
    assert unverified == ["500000 rows processed"]


def test_verify_claims_ignores_empty_claims():
    resume = make_resume()
    verified, unverified = verify_claims(["", "   ", "Python"], resume)
    assert verified == ["Python"]
    assert unverified == []


# ---------------------------------------------------------------------------
# End-to-end agent test with a fake LLM provider (no real API calls)
# ---------------------------------------------------------------------------


class FakeLLMProvider(LLMProvider):
    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMOutreachDraft
        return self._canned_response


def test_agent_draft_end_to_end_with_fake_llm():
    resume = make_resume()
    draft = LLMOutreachDraft(
        subject_line="Interested in your Data Analyst role",
        message_body="Hi there, I'm Test Person, a Data Analyst with Python and SQL experience...",
        claims_referenced=["Python", "SQL", "Kubernetes"],  # Kubernetes is fabricated on purpose
    )
    agent = RecruiterOutreachAgent(llm_provider=FakeLLMProvider(draft))

    result = agent.draft(resume, "Some job description text.", recruiter_name="Jordan")

    assert result.subject_line == "Interested in your Data Analyst role"
    assert "Python" in result.verified_claims
    assert "SQL" in result.verified_claims
    assert "Kubernetes" in result.unverified_claims


def test_agent_draft_with_no_claims_has_no_unverified():
    resume = make_resume()
    draft = LLMOutreachDraft(
        subject_line="Quick intro",
        message_body="Hi there, I'd love to connect about the role.",
        claims_referenced=[],
    )
    agent = RecruiterOutreachAgent(llm_provider=FakeLLMProvider(draft))

    result = agent.draft(resume, "Some job description text.")

    assert result.verified_claims == []
    assert result.unverified_claims == []
