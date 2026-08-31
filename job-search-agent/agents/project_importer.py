"""
agents/project_importer.py
-----------------------------
The GitHub Project Importer: turns one of your real public GitHub repos
into a draft resume Project entry (name, description, bullets,
technologies) -- grounded entirely in what's actually in the repo (its
description, README, language, topics), never invented.

DESIGN, IN ONE PARAGRAPH:
Like the Recruiter Outreach Agent, this has to generate real prose (a
project description, bullet points) -- there's no way to draft a project
entry by only reordering existing resume text, because this project isn't
in your resume yet. So the LLM only ever works from the repo's own real
content (fetched fresh from GitHub, not from training data or guesses),
and every specific claim it writes is checked against that SAME repo data
afterward via `verify_claims_against_text` -- so a claim that isn't
actually backed by the repo (a technology it doesn't use, a metric the
README never mentions) gets flagged for you, exactly like the outreach
agent's fact-check.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agents.fact_checking import verify_claims_against_text
from config.logging_setup import get_logger
from integrations.llm.base import LLMError, LLMProvider
from resume.schema import Project

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# What we ask the LLM to return.
# ---------------------------------------------------------------------------


class LLMProjectDraft(BaseModel):
    name: str
    description: str
    bullets: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    claims_referenced: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class ImportedProjectResult(BaseModel):
    project: Project  # ready to save, or to append to your master resume
    verified_claims: list[str]
    unverified_claims: list[str]


class ProjectImportError(Exception):
    """Raised when the Project Importer can't produce a draft at all
    (wraps underlying LLM or GitHub errors with agent-level context)."""


def build_repo_source_text(repo: dict, readme_text: str | None) -> str:
    """
    Every real, checkable fact about the repo, flattened into one blob --
    this is the ground truth `verify_claims_against_text` checks the
    LLM's claims against (NOT your resume, since this project isn't in
    your resume yet).
    """
    parts = [
        repo.get("name", "") or "",
        repo.get("description") or "",
        repo.get("language") or "",
        " ".join(repo.get("topics", []) or []),
        str(repo.get("stargazers_count", "") or ""),
        readme_text or "",
    ]
    return " | ".join(p for p in parts if p)


class ProjectImportAgent:
    """
    Usage:
        agent = ProjectImportAgent(llm_provider)
        result = agent.import_repo(repo, readme_text)
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def import_repo(self, repo: dict, readme_text: str | None) -> ImportedProjectResult:
        from prompts.project_import_prompts import SYSTEM_PROMPT, build_user_prompt

        try:
            draft = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(repo, readme_text),
                output_model=LLMProjectDraft,
            )
        except LLMError as e:
            logger.error("Project Importer: LLM call failed: %s", e)
            raise ProjectImportError(f"Could not draft a project entry: {e}") from e

        source_text = build_repo_source_text(repo, readme_text)
        verified, unverified = verify_claims_against_text(draft.claims_referenced, source_text)

        project = Project(
            name=draft.name,
            description=draft.description,
            bullets=draft.bullets,
            technologies=draft.technologies,
            url=repo.get("html_url"),
        )

        result = ImportedProjectResult(
            project=project, verified_claims=verified, unverified_claims=unverified
        )

        if unverified:
            logger.warning(
                "Project import draft has %d unverified claim(s): %s", len(unverified), unverified
            )
        logger.info(
            "Project imported | name=%s claims=%d verified=%d unverified=%d",
            draft.name,
            len(draft.claims_referenced),
            len(verified),
            len(unverified),
        )
        return result
