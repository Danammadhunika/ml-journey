"""
tests/test_job_matcher.py
---------------------------
Tests for the Job Matching Agent.

These are split into two groups:
  1. Tests for the deterministic scoring functions — pure Python, no LLM
     involved at all. These are the tests that matter most: they prove the
     score is reproducible and matches the weights in scoring_config.py.
  2. One end-to-end test of `JobMatchingAgent.evaluate()` using a fake
     LLM provider (a stand-in that returns a canned answer instead of
     calling the real Anthropic API) — this proves the agent correctly
     assembles a MatchResult from an LLM analysis, without spending money
     or requiring network access / a real API key.
"""

import pytest

from agents import scoring_config as cfg
from agents.job_matcher import (
    JobMatchingAgent,
    LLMJobAnalysis,
    determine_recommendation,
    determine_sponsorship,
    score_education,
    score_experience,
    score_location,
    score_seniority,
    score_technical_skills,
)
from integrations.llm.base import LLMProvider
from resume.schema import ContactInfo, Education, Experience, MasterResume

# ---------------------------------------------------------------------------
# A minimal resume fixture, reused across tests.
# ---------------------------------------------------------------------------


def make_resume(**overrides) -> MasterResume:
    defaults = dict(
        contact=ContactInfo(
            name="Test Person",
            email="test@example.com",
            location="Connecticut, USA",
            work_authorization="STEM OPT — authorized to work in the US",
        ),
        summary="A test summary.",
        skills=["Python", "SQL", "FastAPI"],
        experience=[
            Experience(
                company="Test Co",
                client=None,
                title="Data Analyst",
                start_date="Jan 2023",
                end_date="Jan 2025",  # fixed dates -> deterministic ~2.0 years
                bullets=["Did analyst things."],
            )
        ],
        education=[
            Education(
                institution="Test University",
                degree="Master of Science",
                field_of_study="Computer Science",
            )
        ],
    )
    defaults.update(overrides)
    return MasterResume(**defaults)


def make_analysis(**overrides) -> LLMJobAnalysis:
    defaults = dict(
        required_skills=["Python", "SQL"],
        preferred_skills=["AWS"],
        matched_required_skills=["Python", "SQL"],
        matched_preferred_skills=[],
        missing_preferred_skills=["AWS"],
        min_years_experience=2.0,
        education_requirement="Bachelor's degree in Computer Science",
        seniority_level="JUNIOR",
        location_text="Hartford, CT",
        remote_option=False,
        sponsorship_signal="NOT_MENTIONED",
        summary_reason="Good overall fit.",
    )
    defaults.update(overrides)
    return LLMJobAnalysis(**defaults)


# ---------------------------------------------------------------------------
# Deterministic scoring functions
# ---------------------------------------------------------------------------


def test_weights_sum_to_one():
    assert sum(cfg.SCORE_WEIGHTS.values()) == pytest.approx(1.0)


def test_score_technical_skills_full_match():
    analysis = make_analysis(
        required_skills=["Python", "SQL"],
        matched_required_skills=["Python", "SQL"],
        preferred_skills=[],
        matched_preferred_skills=[],
    )
    assert score_technical_skills(analysis) == 100


def test_score_technical_skills_partial_match():
    analysis = make_analysis(
        required_skills=["Python", "SQL", "Go"],
        matched_required_skills=["Python", "SQL"],  # 2/3 required
        preferred_skills=["AWS"],
        matched_preferred_skills=[],  # 0/1 preferred
    )
    # 2/3 * 80 + 0/1 * 20 = 53.33 -> rounds to 53
    assert score_technical_skills(analysis) == 53


def test_score_technical_skills_no_requirements_listed():
    analysis = make_analysis(required_skills=[], preferred_skills=[])
    assert score_technical_skills(analysis) == 100


def test_score_experience_meets_requirement():
    assert score_experience(candidate_years=5.0, min_years_required=3.0) == 100


def test_score_experience_below_requirement():
    # 1 year of experience against a 2-year requirement -> 50/100
    assert score_experience(candidate_years=1.0, min_years_required=2.0) == 50


def test_score_experience_no_requirement_stated():
    assert score_experience(candidate_years=0.5, min_years_required=None) == 100


def test_score_education_meets_requirement():
    resume = make_resume()  # has a Master's
    assert score_education(resume, "Bachelor's degree required") == 100


def test_score_education_gap():
    resume = make_resume(
        education=[Education(institution="X", degree="Bachelor of Science", field_of_study="CS")]
    )
    score = score_education(resume, "PhD required")
    assert score < 100  # Bachelor's vs PhD is a real gap


def test_score_education_not_specified_in_job():
    resume = make_resume()
    assert score_education(resume, None) == 100


def test_score_seniority_exact_match():
    # ~2 years of experience -> JUNIOR bucket
    assert score_seniority(candidate_years=2.0, job_seniority_level="JUNIOR") == 100


def test_score_seniority_mismatch():
    score = score_seniority(candidate_years=1.0, job_seniority_level="STAFF_OR_ABOVE")
    assert score < 100


def test_score_seniority_not_specified():
    assert score_seniority(candidate_years=1.0, job_seniority_level="NOT_SPECIFIED") == 100


def test_score_location_remote():
    analysis = make_analysis(remote_option=True, location_text="Anywhere, Mars")
    assert score_location(analysis) == 100


def test_score_location_in_target_region():
    analysis = make_analysis(remote_option=False, location_text="Hartford, CT")
    assert score_location(analysis) == 100


def test_score_location_out_of_region():
    analysis = make_analysis(remote_option=False, location_text="Austin, TX")
    assert score_location(analysis) == 50


def test_score_location_not_specified():
    analysis = make_analysis(remote_option=False, location_text=None)
    assert score_location(analysis) == 100


def test_sponsorship_not_mentioned_is_unknown():
    resume = make_resume()
    analysis = make_analysis(sponsorship_signal="NOT_MENTIONED")
    label, note = determine_sponsorship(resume, analysis)
    assert label == "UNKNOWN"
    assert note is None


def test_sponsorship_no_sponsorship_stated_is_potential_concern_and_quotes_verbatim():
    resume = make_resume()
    analysis = make_analysis(
        sponsorship_signal="NO_SPONSORSHIP_STATED",
        sponsorship_quote="Must be authorized to work without sponsorship.",
    )
    label, note = determine_sponsorship(resume, analysis)
    assert label == "POTENTIAL_CONCERN"
    # The candidate's exact resume wording must appear, unmodified.
    assert "STEM OPT — authorized to work in the US" in note
    assert "Must be authorized to work without sponsorship." in note
    assert "not legal" in note.lower()


def test_sponsorship_available_is_compatible():
    resume = make_resume()
    analysis = make_analysis(
        sponsorship_signal="SPONSORSHIP_AVAILABLE",
        sponsorship_quote="We sponsor H-1B visas.",
    )
    label, note = determine_sponsorship(resume, analysis)
    assert label == "COMPATIBLE"


def test_recommendation_thresholds():
    assert determine_recommendation(85, "UNKNOWN")[0] == "APPLY"
    assert determine_recommendation(70, "UNKNOWN")[0] == "REVIEW"
    assert determine_recommendation(40, "UNKNOWN")[0] == "SKIP"


def test_recommendation_downgrades_on_sponsorship_concern():
    recommendation, notes = determine_recommendation(90, "POTENTIAL_CONCERN")
    assert recommendation == "REVIEW"
    assert notes  # a downgrade reason should be recorded


# ---------------------------------------------------------------------------
# End-to-end agent test with a fake LLM provider (no real API calls)
# ---------------------------------------------------------------------------


class FakeLLMProvider(LLMProvider):
    """A stand-in LLM that returns a pre-built analysis instead of calling
    a real API. Lets us test the agent's assembly logic in isolation."""

    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMJobAnalysis
        return self._canned_response


def test_agent_evaluate_end_to_end_with_fake_llm():
    resume = make_resume()
    analysis = make_analysis(
        required_skills=["Python", "SQL"],
        matched_required_skills=["Python", "SQL"],
        preferred_skills=[],
        matched_preferred_skills=[],
        min_years_experience=1.0,  # resume has ~2.0 years -> meets it
        education_requirement="Bachelor's degree required",
        seniority_level="JUNIOR",
        location_text="Hartford, CT",
        sponsorship_signal="NOT_MENTIONED",
        strengths_notes=["Strong Python and SQL background."],
        gaps_notes=[],
        summary_reason="Strong technical and experience match.",
    )
    agent = JobMatchingAgent(llm_provider=FakeLLMProvider(analysis))

    result = agent.evaluate(resume, "Some job description text.")

    assert result.technical_skills_score == 100
    assert result.experience_score == 100
    assert result.education_score == 100
    assert result.seniority_score == 100
    assert result.location_score == 100
    assert result.overall_score == 100
    assert result.recommendation == "APPLY"
    assert result.sponsorship_compatibility == "UNKNOWN"
    assert result.strengths == ["Strong Python and SQL background."]
