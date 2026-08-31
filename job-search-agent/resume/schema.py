"""
resume/schema.py
----------------
Defines the SHAPE of your resume as Python classes (Pydantic models).

WHY THIS FILE EXISTS:
Every agent in this system (matching, tailoring, cover letters) needs to
read your resume in a predictable structure. If we just passed around a
raw dict or a block of text, one typo in a field name ("skil" vs "skill")
could silently break things. Pydantic models act like a strict contract:
if your master_resume.json doesn't match this shape, you get a clear error
the moment you load it — not a weird bug three steps later.

Think of each `class` below as a form with specific fields. `BaseModel`
(from Pydantic) gives us free validation, JSON parsing, and helpful error
messages just by inheriting from it.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactInfo(BaseModel):
    """Your contact details, as they should appear on a resume."""

    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None  # e.g. "Milford, CT" or "United States"
    # Short line under your name, e.g. "Python Developer · Data Analyst · ML Engineer"
    headline: Optional[str] = None
    # Verbatim work-authorization line, e.g. "STEM OPT — authorized to work in the US".
    # Kept as free text (never inferred/guessed) because the Job Matching Agent's
    # "sponsorship compatibility" score and any legal/immigration question always
    # need your EXACT stated wording, not a paraphrase.
    work_authorization: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class Experience(BaseModel):
    """One job in your work history.

    `company` is always your actual EMPLOYER OR CONSULTANCY — the entity
    that hired/paid you. `client` is optional and separate: for consulting
    / staffing arrangements, it's the end client you were placed with or
    did the work for. The two are never merged into one string, so nothing
    downstream (resume tailoring, cover letters, the tracker) can blur who
    your employer was vs. who the client was.
    """

    company: str  # Employer / consultancy name — never replaced by the client name.
    client: Optional[str] = None  # End client, if this was a consulting/staffing placement.
    title: str
    location: Optional[str] = None
    start_date: str  # kept as free text ("Jan 2024") so you don't have to
    end_date: str  # fight date parsing for a v1 project. Use "Present" for
    #                 a current role.
    bullets: list[str] = Field(default_factory=list)
    # ^ Each bullet is one truthful accomplishment/responsibility line.
    # The Resume Tailoring Agent (built later) is only ever allowed to
    # REORDER or REWORD these bullets for emphasis — never invent a new one.


class Education(BaseModel):
    """One degree/program."""

    institution: str
    degree: str  # e.g. "Master of Science"
    field_of_study: str  # e.g. "Computer Science"
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None


class Project(BaseModel):
    """A portfolio / personal project worth highlighting."""

    name: str
    description: str
    bullets: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    url: Optional[str] = None


class Certification(BaseModel):
    """A certification or credential."""

    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None


class MasterResume(BaseModel):
    """
    The full resume — this is the single SOURCE OF TRUTH object that every
    other agent (matcher, tailoring agent, cover letter agent) will read
    from. Nothing downstream is ever allowed to add information that isn't
    already represented here.
    """

    contact: ContactInfo
    summary: str
    # Flat skill list (used for quick keyword matching):
    skills: list[str] = Field(default_factory=list)
    # Optional grouping for nicer resume rendering, e.g.
    # {"Languages": ["Python", "SQL"], "Cloud": ["AWS", "Docker"]}
    skill_categories: dict[str, list[str]] = Field(default_factory=dict)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)

    def all_skill_terms(self) -> set[str]:
        """
        Convenience helper: every skill keyword we truthfully know about,
        lower-cased, gathered from both the flat list and the categorized
        dict. Later, the Job Matching Agent uses this to check "does the
        job's required skill list overlap with something Madhu actually
        has?" without duplicating this logic in every agent.
        """
        terms = {s.lower() for s in self.skills}
        for group_terms in self.skill_categories.values():
            terms.update(t.lower() for t in group_terms)
        return terms
