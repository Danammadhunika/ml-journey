"""
tests/test_cover_letter.py
------------------------------
Tests for the Cover Letter Agent.

No real Anthropic API calls: uses a fake LLM provider so this runs
offline and fast, matching tests/test_recruiter_outreach.py.
"""

from agents.cover_letter import (
    CoverLetterAgent,
    LLMCoverLetterDraft,
    build_resume_summary_text,
)
from integrations.llm.base import LLMProvider
from resume.schema import ContactInfo, Experience, MasterResume

FAKE_RESUME = MasterResume(
    contact=ContactInfo(
        name="Madhu Danam",
        email="madhu@example.com",
        headline="Python Developer",
        work_authorization="STEM OPT -- authorized to work in the US",
    ),
    summary="Backend-focused Python developer with SQL and cloud experience.",
    skills=["Python", "SQL", "AWS"],
    experience=[
        Experience(
            company="Acme Corp",
            title="Software Engineer",
            start_date="Jan 2023",
            end_date="Present",
            bullets=["Built REST APIs serving 10000 requests per day."],
        )
    ],
)

FAKE_JOB_DESCRIPTION = "We are looking for a Python developer with SQL and AWS experience."


def test_build_resume_summary_text_excludes_work_authorization():
    text = build_resume_summary_text(FAKE_RESUME)
    assert "STEM OPT" not in text
    assert "Python" in text


class FakeLLMProvider(LLMProvider):
    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMCoverLetterDraft
        return self._canned_response


def test_agent_draft_end_to_end_with_fake_llm():
    draft = LLMCoverLetterDraft(
        greeting="Dear Hiring Manager,",
        opening_paragraph="I'm excited to apply for the Python Developer role at Acme.",
        body_paragraphs=[
            "In my current role as a Software Engineer at Acme Corp, I built REST APIs "
            "serving 10000 requests per day using Python and SQL.",
            "I also have hands-on experience with AWS.",
        ],
        closing_paragraph="I'd welcome the chance to discuss how I could contribute.",
        claims_referenced=["Python", "SQL", "AWS", "Acme Corp", "10000 requests", "Kubernetes"],
    )
    agent = CoverLetterAgent(llm_provider=FakeLLMProvider(draft))

    result = agent.draft(FAKE_RESUME, FAKE_JOB_DESCRIPTION, company_name="Acme")

    assert "Python" in result.verified_claims
    assert "Acme Corp" in result.verified_claims
    assert "Kubernetes" in result.unverified_claims
    assert "Dear Hiring Manager," in result.full_text
    assert "STEM OPT" not in result.full_text
