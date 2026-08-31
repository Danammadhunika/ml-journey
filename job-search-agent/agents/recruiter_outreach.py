"""
agents/recruiter_outreach.py
-------------------------------
The Recruiter Outreach Agent: drafts a short message to a recruiter about
a specific job -- a DRAFT ONLY. This project has no email/LinkedIn
integration, so nothing this agent produces is ever sent anywhere by the
code itself; you always copy, review, and send it yourself.

DESIGN, IN ONE PARAGRAPH:
Unlike the Job Matching Agent and Resume Tailoring Agent, this one has to
let the LLM write real, original sentences -- there's no way to draft an
outreach message by only reordering existing text. So instead of making
fabrication structurally impossible, this agent adds a verification step:
the LLM must separately list every specific factual claim it used in the
message (`claims_referenced`), and `verify_claims()` independently checks
each one against your actual resume afterward. Anything that doesn't
check out is flagged for you to review -- it's never silently removed or
"corrected," because only you can judge exactly what's wrong and fix it.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from config.logging_setup import get_logger
from integrations.llm.base import LLMError, LLMProvider
from resume.schema import MasterResume

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# What we ask the LLM to return.
# ---------------------------------------------------------------------------


class LLMOutreachDraft(BaseModel):
    subject_line: str
    message_body: str
    claims_referenced: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class OutreachResult(BaseModel):
    subject_line: str
    message_body: str
    verified_claims: list[str]
    unverified_claims: list[str]


class RecruiterOutreachError(Exception):
    """Raised when the Recruiter Outreach Agent can't produce a draft at all
    (wraps underlying LLM errors with agent-level context)."""


# ---------------------------------------------------------------------------
# Deterministic claim verification -- pure Python, unit-testable without
# ever calling an LLM.
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Lowercase and strip everything except letters, digits, and a few
    characters that matter for numbers/percentages, so "541,909" and
    "541909" or "3.767/4.0 GPA" and "3.767 gpa" compare sensibly."""
    return re.sub(r"[^a-z0-9.%/ ]", "", text.lower())


def _resume_haystack(resume: MasterResume) -> str:
    """Every true fact in the resume, flattened into one lowercased blob
    of text to check claims against. Deliberately over-inclusive (every
    field, not just skills) since a claim might reference an employer
    name, a degree, or a project metric just as easily as a skill."""
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
    return _normalize(" | ".join(p for p in parts if p))


def verify_claims(claims: list[str], resume: MasterResume) -> tuple[list[str], list[str]]:
    """
    Splits `claims` into (verified, unverified) against the resume's real
    content. A claim is "verified" if:
      - it appears near-verbatim in the resume, or
      - it contains a number (a GPA, a metric, a count) and that exact
        number appears somewhere in the resume -- numbers are the most
        distinctive, hardest-to-fake part of a claim, so we trust a
        number match even if a generic descriptor word around it (like
        "GPA" or "rows") doesn't itself appear anywhere verbatim, or
      - it has no number, and at least half of its significant words
        (ignoring short filler words) show up somewhere in the resume.

    This is deliberately generous -- the goal is to catch clear
    fabrications (a skill, employer, or metric that's simply not in the
    resume), not to penalize the LLM for normal, true rephrasing.
    Anything unverified is a signal to double-check, never proof of a lie
    (and never silently removed -- only you can judge and fix it).
    """
    haystack = _resume_haystack(resume)
    verified: list[str] = []
    unverified: list[str] = []

    for claim in claims:
        normalized_claim = _normalize(claim).strip()
        if not normalized_claim:
            continue
        if normalized_claim in haystack:
            verified.append(claim)
            continue

        significant_words = [w for w in normalized_claim.split() if len(w) > 2]
        if not significant_words:
            unverified.append(claim)
            continue

        numeric_words = [w for w in significant_words if any(ch.isdigit() for ch in w)]
        if numeric_words:
            is_verified = all(word in haystack for word in numeric_words)
        else:
            matched = [w for w in significant_words if w in haystack]
            is_verified = len(matched) >= max(1, (len(significant_words) + 1) // 2)

        if is_verified:
            verified.append(claim)
        else:
            unverified.append(claim)

    return verified, unverified


# ---------------------------------------------------------------------------
# The agent itself.
# ---------------------------------------------------------------------------


class RecruiterOutreachAgent:
    """
    Usage:
        agent = RecruiterOutreachAgent(llm_provider)
        result = agent.draft(resume, job_description_text, recruiter_name="Jordan")
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def draft(
        self,
        resume: MasterResume,
        job_description_text: str,
        recruiter_name: str | None = None,
    ) -> OutreachResult:
        from prompts.recruiter_outreach_prompts import SYSTEM_PROMPT, build_user_prompt

        try:
            draft = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(resume, job_description_text, recruiter_name),
                output_model=LLMOutreachDraft,
            )
        except LLMError as e:
            logger.error("Recruiter Outreach Agent: LLM call failed: %s", e)
            raise RecruiterOutreachError(f"Could not draft an outreach message: {e}") from e

        verified, unverified = verify_claims(draft.claims_referenced, resume)

        result = OutreachResult(
            subject_line=draft.subject_line,
            message_body=draft.message_body,
            verified_claims=verified,
            unverified_claims=unverified,
        )

        if unverified:
            logger.warning(
                "Recruiter outreach draft has %d unverified claim(s): %s",
                len(unverified),
                unverified,
            )
        logger.info(
            "Recruiter outreach drafted | claims=%d verified=%d unverified=%d",
            len(draft.claims_referenced),
            len(verified),
            len(unverified),
        )
        return result
