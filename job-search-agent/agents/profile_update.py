"""
agents/profile_update.py
----------------------------
The Resume/LinkedIn Update Drafter: given your real resume plus one new
"highlight" (freeform text about something you just learned/built, or a
project you already imported with the GitHub Project Importer), drafts:
  - an updated LinkedIn "About" section (the full section, ready to
    review and paste in yourself), and
  - a short standalone "what's new" blurb about just the highlight.

DRAFT ONLY: this project has no LinkedIn integration, so nothing this
agent produces is ever posted, edited, or sent anywhere by the code
itself -- you always copy, review, and update your real LinkedIn profile
yourself.

DESIGN, IN ONE PARAGRAPH:
Same pattern as the Recruiter Outreach Agent and the GitHub Project
Importer: the LLM has to write real, original prose here (an About
section isn't something you can build by just reordering existing text),
so instead of making fabrication structurally impossible, this agent
adds a verification step. The LLM must separately list every specific
factual claim it used (`claims_referenced`), and
`verify_claims_against_text` (the same shared helper the Project
Importer uses) independently checks each one against a haystack built
from BOTH your real resume AND the highlight text you gave it. Anything
that doesn't check out is flagged for you to review -- never silently
removed or "corrected."
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agents.fact_checking import verify_claims_against_text
from config.logging_setup import get_logger
from integrations.llm.base import LLMError, LLMProvider
from resume.schema import MasterResume

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# What we ask the LLM to return.
# ---------------------------------------------------------------------------


class LLMProfileUpdateDraft(BaseModel):
    linkedin_about: str
    whats_new_blurb: str
    claims_referenced: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class ProfileUpdateResult(BaseModel):
    linkedin_about: str
    whats_new_blurb: str
    verified_claims: list[str]
    unverified_claims: list[str]


class ProfileUpdateError(Exception):
    """Raised when the Profile Update Drafter can't produce a draft at all
    (wraps underlying LLM errors with agent-level context)."""


# ---------------------------------------------------------------------------
# Building the resume side of the fact-check haystack. Deliberately
# excludes contact.work_authorization -- Hard Rule 4 in the prompt already
# tells the LLM never to mention sponsorship/visa status here, and leaving
# that field out of the haystack means even an accidental mention could
# never accidentally get "verified".
# ---------------------------------------------------------------------------


def build_resume_summary_text(resume: MasterResume) -> str:
    """Every true, non-sensitive resume fact, flattened into one blob --
    used both as what we show the LLM (so it has real facts to draw on)
    and, combined with the highlight text, as the fact-check haystack."""
    parts: list[str] = [resume.summary, resume.contact.name, resume.contact.headline or ""]
    parts.extend(resume.skills)
    for group in resume.skill_categories.values():
        parts.extend(group)
    for exp in resume.experience:
        parts.extend([exp.company, exp.client or "", exp.title])
        parts.extend(exp.bullets)
    for edu in resume.education:
        parts.extend([edu.institution, edu.degree, edu.field_of_study, edu.gpa or ""])
    for project in resume.projects:
        parts.extend([project.name, project.description])
        parts.extend(project.bullets)
        parts.extend(project.technologies)
    for cert in resume.certifications:
        parts.extend([cert.name, cert.issuer or ""])
    return " | ".join(p for p in parts if p)


class ProfileUpdateAgent:
    """
    Usage:
        agent = ProfileUpdateAgent(llm_provider)
        result = agent.draft(resume, highlight_text)
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def draft(self, resume: MasterResume, highlight_text: str) -> ProfileUpdateResult:
        from prompts.profile_update_prompts import SYSTEM_PROMPT, build_user_prompt

        resume_summary_text = build_resume_summary_text(resume)

        try:
            draft = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(resume_summary_text, highlight_text),
                output_model=LLMProfileUpdateDraft,
            )
        except LLMError as e:
            logger.error("Profile Update Drafter: LLM call failed: %s", e)
            raise ProfileUpdateError(f"Could not draft a profile update: {e}") from e

        haystack = f"{resume_summary_text} | {highlight_text}"
        verified, unverified = verify_claims_against_text(draft.claims_referenced, haystack)

        result = ProfileUpdateResult(
            linkedin_about=draft.linkedin_about,
            whats_new_blurb=draft.whats_new_blurb,
            verified_claims=verified,
            unverified_claims=unverified,
        )

        if unverified:
            logger.warning(
                "Profile update draft has %d unverified claim(s): %s", len(unverified), unverified
            )
        logger.info(
            "Profile update drafted | claims=%d verified=%d unverified=%d",
            len(draft.claims_referenced),
            len(verified),
            len(unverified),
        )
        return result
