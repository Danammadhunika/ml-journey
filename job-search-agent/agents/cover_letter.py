"""
agents/cover_letter.py
--------------------------
The Cover Letter Agent: drafts a cover letter for one specific job --
a DRAFT ONLY, exactly like the Recruiter Outreach Agent and the Profile
Update Drafter. This project has no submission integration, so nothing
this agent produces is ever sent or submitted anywhere by the code
itself; you always copy, review, and submit it yourself.

DESIGN, IN ONE PARAGRAPH:
Same pattern as every other agent that has to write real, original prose
(Recruiter Outreach, Project Importer, Profile Update Drafter): the LLM
must separately list every specific factual claim it used
(`claims_referenced`), and the shared `verify_claims_against_text` helper
independently checks each one against your actual resume afterward.
Anything that doesn't check out is flagged for you to review -- never
silently removed or "corrected."
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


class LLMCoverLetterDraft(BaseModel):
    greeting: str
    opening_paragraph: str
    body_paragraphs: list[str] = Field(default_factory=list)
    closing_paragraph: str
    claims_referenced: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class CoverLetterResult(BaseModel):
    full_text: str
    verified_claims: list[str]
    unverified_claims: list[str]


class CoverLetterError(Exception):
    """Raised when the Cover Letter Agent can't produce a draft at all
    (wraps underlying LLM errors with agent-level context)."""


# ---------------------------------------------------------------------------
# Building the fact-check haystack. Deliberately excludes
# contact.work_authorization -- Hard Rule 5 in the prompt already tells
# the LLM never to mention sponsorship/visa status in a cover letter, and
# leaving that field out of the haystack means even an accidental mention
# could never accidentally get "verified".
# ---------------------------------------------------------------------------


def build_resume_summary_text(resume: MasterResume) -> str:
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


def _assemble_full_text(draft: LLMCoverLetterDraft) -> str:
    paragraphs = [draft.greeting, "", draft.opening_paragraph, ""]
    for body in draft.body_paragraphs:
        paragraphs.append(body)
        paragraphs.append("")
    paragraphs.append(draft.closing_paragraph)
    return "\n".join(paragraphs).strip() + "\n"


class CoverLetterAgent:
    """
    Usage:
        agent = CoverLetterAgent(llm_provider)
        result = agent.draft(resume, job_description_text, company_name="Acme", hiring_manager_name="Jordan")
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def draft(
        self,
        resume: MasterResume,
        job_description_text: str,
        company_name: str | None = None,
        hiring_manager_name: str | None = None,
    ) -> CoverLetterResult:
        from prompts.cover_letter_prompts import SYSTEM_PROMPT, build_user_prompt

        resume_summary_text = build_resume_summary_text(resume)

        try:
            draft = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(
                    resume_summary_text, job_description_text, company_name, hiring_manager_name
                ),
                output_model=LLMCoverLetterDraft,
            )
        except LLMError as e:
            logger.error("Cover Letter Agent: LLM call failed: %s", e)
            raise CoverLetterError(f"Could not draft a cover letter: {e}") from e

        verified, unverified = verify_claims_against_text(draft.claims_referenced, resume_summary_text)

        result = CoverLetterResult(
            full_text=_assemble_full_text(draft),
            verified_claims=verified,
            unverified_claims=unverified,
        )

        if unverified:
            logger.warning(
                "Cover letter draft has %d unverified claim(s): %s", len(unverified), unverified
            )
        logger.info(
            "Cover letter drafted | claims=%d verified=%d unverified=%d",
            len(draft.claims_referenced),
            len(verified),
            len(unverified),
        )
        return result
