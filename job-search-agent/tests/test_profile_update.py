"""
tests/test_profile_update.py
--------------------------------
Tests for the Resume/LinkedIn Update Drafter.

No real Anthropic API calls: uses a fake LLM provider so this runs
offline and fast, exactly like tests/test_recruiter_outreach.py and
tests/test_project_importer.py.
"""

from agents.profile_update import (
    LLMProfileUpdateDraft,
    ProfileUpdateAgent,
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

FAKE_HIGHLIGHT = (
    "Just built a movie recommendation app using Python, Pandas, and "
    "Scikit-learn, trained on the MovieLens 100K dataset, deployed with "
    "Streamlit."
)


def test_build_resume_summary_text_includes_real_facts():
    text = build_resume_summary_text(FAKE_RESUME)
    assert "Python" in text
    assert "Acme Corp" in text
    assert "10000 requests" in text


def test_build_resume_summary_text_excludes_work_authorization():
    # Hard Rule 4 says the LLM should never mention sponsorship/visa
    # status in a profile update -- leaving it out of the haystack means
    # an accidental mention could never accidentally get "verified".
    text = build_resume_summary_text(FAKE_RESUME)
    assert "STEM OPT" not in text


class FakeLLMProvider(LLMProvider):
    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMProfileUpdateDraft
        return self._canned_response


def test_agent_draft_end_to_end_with_fake_llm():
    draft = LLMProfileUpdateDraft(
        linkedin_about=(
            "I'm a backend-focused Python developer with experience in SQL "
            "and AWS. I recently built a movie recommendation app using "
            "Python, Pandas, and Scikit-learn, deployed with Streamlit."
        ),
        whats_new_blurb=(
            "I just built a movie recommendation app trained on the "
            "MovieLens 100K dataset and deployed it with Streamlit."
        ),
        claims_referenced=[
            "Python",
            "AWS",
            "Scikit-learn",
            "MovieLens 100K",
            "Kubernetes",
        ],
    )
    agent = ProfileUpdateAgent(llm_provider=FakeLLMProvider(draft))

    result = agent.draft(FAKE_RESUME, FAKE_HIGHLIGHT)

    assert "Python" in result.verified_claims
    assert "Scikit-learn" in result.verified_claims
    assert "Kubernetes" in result.unverified_claims
    assert "movie recommendation app" in result.linkedin_about.lower()
