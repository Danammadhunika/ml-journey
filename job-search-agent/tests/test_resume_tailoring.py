"""
tests/test_resume_tailoring.py
--------------------------------
Tests for the Resume Tailoring Agent.

Same split as tests/test_job_matcher.py:
  1. Deterministic reordering functions -- pure Python, no LLM.
  2. One end-to-end test of `ResumeTailoringAgent.tailor()` using a fake
     LLM provider (no real API calls).

The single most important test here is
`test_build_tailored_resume_never_adds_or_removes_bullets_or_skills`,
which proves the core safety guarantee of this agent: tailoring can only
ever reorder your real content, never invent or drop any of it.
"""

import pytest

from agents.resume_tailoring import (
    BulletRelevance,
    LLMTailoringAnalysis,
    ResumeTailoringAgent,
    build_tailored_resume,
    reorder_bullets,
    reorder_skills,
)
from integrations.llm.base import LLMProvider
from resume.schema import ContactInfo, Education, Experience, MasterResume


def make_resume(**overrides) -> MasterResume:
    defaults = dict(
        contact=ContactInfo(name="Test Person", email="test@example.com"),
        summary="A test summary.",
        skills=["Python", "SQL", "AWS", "Docker"],
        experience=[
            Experience(
                company="Company A",
                client="Client A",
                title="Data Analyst",
                start_date="Jan 2023",
                end_date="Present",
                bullets=[
                    "Wrote Python scripts for data pipelines.",
                    "Built dashboards in Tableau.",
                    "Queried databases with SQL joins and aggregations.",
                ],
            ),
            Experience(
                company="Company B",
                client=None,
                title="Junior Analyst",
                start_date="Jan 2021",
                end_date="Dec 2022",
                bullets=[
                    "Maintained spreadsheets.",
                    "Automated reports with Python.",
                ],
            ),
        ],
        education=[
            Education(institution="Test University", degree="B.S.", field_of_study="CS")
        ],
    )
    defaults.update(overrides)
    return MasterResume(**defaults)


# ---------------------------------------------------------------------------
# Deterministic reordering functions
# ---------------------------------------------------------------------------


def test_reorder_skills_moves_matches_to_front_without_changing_the_set():
    skills = ["Python", "SQL", "AWS", "Docker"]
    reordered = reorder_skills(skills, required_skills=["AWS"], preferred_skills=["Docker"])
    assert reordered[:2] == ["AWS", "Docker"]
    assert set(reordered) == set(skills)  # nothing added or dropped
    assert len(reordered) == len(skills)  # nothing duplicated either


def test_reorder_skills_preserves_original_order_within_each_group():
    skills = ["Python", "SQL", "AWS", "Docker"]
    # Nothing in the JD -> no group is "relevant", stable sort keeps order.
    reordered = reorder_skills(skills, required_skills=[], preferred_skills=[])
    assert reordered == skills


def test_reorder_bullets_sorts_by_score_descending():
    bullets = ["low relevance", "high relevance", "medium relevance"]
    reordered = reorder_bullets(bullets, {0: 10, 1: 90, 2: 50})
    assert reordered == ["high relevance", "medium relevance", "low relevance"]


def test_reorder_bullets_never_drops_an_unscored_bullet():
    bullets = ["scored", "unscored"]
    reordered = reorder_bullets(bullets, {0: 80})  # index 1 never mentioned
    assert set(reordered) == set(bullets)
    assert len(reordered) == 2


def test_build_tailored_resume_never_adds_or_removes_bullets_or_skills():
    resume = make_resume()
    analysis = LLMTailoringAnalysis(
        required_skills=["Python", "SQL"],
        preferred_skills=[],
        bullet_relevance=[
            BulletRelevance(experience_index=0, bullet_index=2, relevance_score=95),
            BulletRelevance(experience_index=0, bullet_index=0, relevance_score=80),
            BulletRelevance(experience_index=0, bullet_index=1, relevance_score=10),
            BulletRelevance(experience_index=1, bullet_index=1, relevance_score=70),
        ],
        emphasis_notes=["Leading with SQL and Python experience."],
    )

    tailored = build_tailored_resume(resume, analysis)

    # Same set of skills, just reordered.
    assert set(tailored.skills) == set(resume.skills)
    assert tailored.skills[0] in ("Python", "SQL")

    # Same set of bullets per experience entry, just reordered.
    for original_exp, tailored_exp in zip(resume.experience, tailored.experience):
        assert set(tailored_exp.bullets) == set(original_exp.bullets)
        assert len(tailored_exp.bullets) == len(original_exp.bullets)

    # Company/client/title/dates are completely untouched.
    assert tailored.experience[0].company == "Company A"
    assert tailored.experience[0].client == "Client A"
    assert tailored.experience[1].client is None

    # The most relevant bullet in experience[0] should now be first.
    assert tailored.experience[0].bullets[0] == "Queried databases with SQL joins and aggregations."

    # The original resume object itself must be unmodified (deep copy).
    assert resume.experience[0].bullets[0] == "Wrote Python scripts for data pipelines."


def test_build_tailored_resume_with_no_llm_scores_keeps_original_bullet_order():
    resume = make_resume()
    analysis = LLMTailoringAnalysis(required_skills=[], preferred_skills=[], bullet_relevance=[])
    tailored = build_tailored_resume(resume, analysis)
    for original_exp, tailored_exp in zip(resume.experience, tailored.experience):
        assert tailored_exp.bullets == original_exp.bullets


# ---------------------------------------------------------------------------
# End-to-end agent test with a fake LLM provider (no real API calls)
# ---------------------------------------------------------------------------


class FakeLLMProvider(LLMProvider):
    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMTailoringAnalysis
        return self._canned_response


def test_agent_tailor_end_to_end_with_fake_llm():
    resume = make_resume()
    analysis = LLMTailoringAnalysis(
        required_skills=["Python"],
        preferred_skills=["AWS"],
        bullet_relevance=[
            BulletRelevance(experience_index=0, bullet_index=0, relevance_score=90),
        ],
        emphasis_notes=["Leading with Python experience since the job requires it."],
    )
    agent = ResumeTailoringAgent(llm_provider=FakeLLMProvider(analysis))

    result = agent.tailor(resume, "Some job description text.")

    assert result.required_skills == ["Python"]
    assert result.preferred_skills == ["AWS"]
    assert result.emphasis_notes == ["Leading with Python experience since the job requires it."]
    assert result.tailored_resume.contact.name == "Test Person"
    assert set(result.tailored_resume.skills) == set(resume.skills)
