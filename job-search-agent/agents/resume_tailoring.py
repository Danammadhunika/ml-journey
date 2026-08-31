"""
agents/resume_tailoring.py
----------------------------
The Resume Tailoring Agent: reorders your EXISTING skills and bullets to
lead with whatever is most relevant to a specific job -- without ever
inventing, editing, or rewriting a single word of your real resume.

DESIGN, IN ONE PARAGRAPH:
Just like the Job Matching Agent, the LLM here is used only to read and
compare -- never to write your resume for you. It returns a relevance
score (0-100) for each of your existing bullets and a reordering hint for
your skills list; it never returns new bullet text. Python then sorts
your real bullets/skills by those scores. Because the sort only ever
rearranges strings that were already in your resume, it's structurally
impossible for this step to fabricate a qualification -- there is a test
(`test_reordering_never_changes_the_set_of_bullets_or_skills`) that proves
exactly that.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from config.logging_setup import get_logger
from integrations.llm.base import LLMError, LLMProvider
from resume.schema import MasterResume

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# What we ask the LLM to return (relevance ratings only -- see
# prompts/resume_tailoring_prompts.py for the exact instructions given).
# ---------------------------------------------------------------------------


class BulletRelevance(BaseModel):
    experience_index: int
    bullet_index: int
    relevance_score: int = Field(ge=0, le=100)


class LLMTailoringAnalysis(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    bullet_relevance: list[BulletRelevance] = Field(default_factory=list)
    emphasis_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class TailoringResult(BaseModel):
    tailored_resume: MasterResume  # same schema as your master resume -- just reordered
    required_skills: list[str]
    preferred_skills: list[str]
    emphasis_notes: list[str]


class ResumeTailoringError(Exception):
    """Raised when the Resume Tailoring Agent can't produce a result at all
    (wraps underlying LLM errors with agent-level context)."""


# ---------------------------------------------------------------------------
# Deterministic reordering -- pure Python, unit-testable without ever
# calling an LLM. Neither function can add, remove, or edit a string.
# ---------------------------------------------------------------------------


def reorder_skills(
    skills: list[str], required_skills: list[str], preferred_skills: list[str]
) -> list[str]:
    """
    Move skills that overlap with the job's stated required/preferred
    skills to the front. Case-insensitive substring match in either
    direction (same approach as the Job Matching Agent's
    `filter_already_matched_requirements`). A stable sort means: every
    skill you already had is still present exactly once, just possibly
    moved earlier -- nothing is added or dropped.
    """
    wanted = [s.lower() for s in required_skills + preferred_skills if s]

    def is_relevant(skill: str) -> bool:
        skill_lower = skill.lower()
        return any(term in skill_lower or skill_lower in term for term in wanted)

    return sorted(skills, key=lambda s: not is_relevant(s))


def reorder_bullets(bullets: list[str], relevance_by_index: dict[int, int]) -> list[str]:
    """
    Sort bullets within one experience entry by relevance score,
    descending. Bullets the LLM didn't score (missing index, or the LLM
    left one out) sort after the scored ones but are NEVER dropped -- a
    missing score just means "not specifically highlighted," not "erase
    this fact."
    """
    indexed = list(enumerate(bullets))
    indexed.sort(key=lambda pair: -relevance_by_index.get(pair[0], -1))
    return [bullet for _, bullet in indexed]


def build_tailored_resume(resume: MasterResume, analysis: LLMTailoringAnalysis) -> MasterResume:
    """
    Deep-copies the real resume and reorders `skills` and each experience
    entry's `bullets` in place. Every other field (contact info, company,
    client, title, dates, education, projects, certifications) is copied
    through completely untouched.
    """
    tailored = resume.model_copy(deep=True)
    tailored.skills = reorder_skills(resume.skills, analysis.required_skills, analysis.preferred_skills)

    scores_by_experience: dict[int, dict[int, int]] = {}
    for rating in analysis.bullet_relevance:
        scores_by_experience.setdefault(rating.experience_index, {})[
            rating.bullet_index
        ] = rating.relevance_score

    for index, experience in enumerate(tailored.experience):
        experience.bullets = reorder_bullets(
            experience.bullets, scores_by_experience.get(index, {})
        )

    return tailored


# ---------------------------------------------------------------------------
# The agent itself.
# ---------------------------------------------------------------------------


class ResumeTailoringAgent:
    """
    Usage:
        agent = ResumeTailoringAgent(llm_provider)
        result = agent.tailor(resume, job_description_text)
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def tailor(self, resume: MasterResume, job_description_text: str) -> TailoringResult:
        from prompts.resume_tailoring_prompts import SYSTEM_PROMPT, build_user_prompt

        try:
            analysis = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(resume, job_description_text),
                output_model=LLMTailoringAnalysis,
            )
        except LLMError as e:
            logger.error("Resume Tailoring Agent: LLM call failed: %s", e)
            raise ResumeTailoringError(f"Could not tailor a resume for this job: {e}") from e

        tailored_resume = build_tailored_resume(resume, analysis)

        result = TailoringResult(
            tailored_resume=tailored_resume,
            required_skills=analysis.required_skills,
            preferred_skills=analysis.preferred_skills,
            emphasis_notes=analysis.emphasis_notes,
        )

        logger.info(
            "Resume tailored | required_skills=%d preferred_skills=%d bullets_scored=%d",
            len(analysis.required_skills),
            len(analysis.preferred_skills),
            len(analysis.bullet_relevance),
        )
        return result
