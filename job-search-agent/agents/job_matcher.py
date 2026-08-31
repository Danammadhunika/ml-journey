"""
agents/job_matcher.py
-----------------------
The Job Matching Agent: scores a job description against your master
resume on a 0-100 scale, with a transparent breakdown and a recommendation.

DESIGN, IN ONE PARAGRAPH:
The LLM is used ONLY to read the job description and compare it to your
resume semantically (what skills does the JD ask for, which ones does
your resume actually show, what's the seniority level, does it mention
sponsorship). It returns that as a structured `LLMJobAnalysis` object —
not a score. Every number in the final result (technical/experience/
education/seniority/location sub-scores, the weighted overall score, and
the APPLY/REVIEW/SKIP recommendation) is then computed by plain,
inspectable, testable Python using the weights in `scoring_config.py`.
This means: the LLM can't "make up" a score, and you can see exactly why
a job got the number it got.
"""

from pydantic import BaseModel, Field

from agents import scoring_config as cfg
from config.logging_setup import get_logger
from integrations.llm.base import LLMError, LLMProvider
from resume.experience_utils import parse_total_experience_years
from resume.schema import MasterResume

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# What we ask the LLM to return (semantic extraction + comparison only —
# see prompts/job_matching_prompts.py for the exact instructions given).
# ---------------------------------------------------------------------------


class LLMJobAnalysis(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_years_experience: float | None = None
    education_requirement: str | None = None
    seniority_level: str = "NOT_SPECIFIED"  # ENTRY/JUNIOR/MID/SENIOR/STAFF_OR_ABOVE/NOT_SPECIFIED
    location_text: str | None = None
    remote_option: bool = False
    sponsorship_signal: str = "NOT_MENTIONED"  # SPONSORSHIP_AVAILABLE/NO_SPONSORSHIP_STATED/NOT_MENTIONED
    sponsorship_quote: str | None = None
    matched_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    other_important_requirements: list[str] = Field(default_factory=list)
    strengths_notes: list[str] = Field(default_factory=list)
    gaps_notes: list[str] = Field(default_factory=list)
    summary_reason: str = ""


# ---------------------------------------------------------------------------
# What the agent hands back to the rest of the app.
# ---------------------------------------------------------------------------


class MatchResult(BaseModel):
    overall_score: int
    technical_skills_score: int
    experience_score: int
    education_score: int
    seniority_score: int
    location_score: int
    sponsorship_compatibility: str  # COMPATIBLE / POTENTIAL_CONCERN / UNKNOWN
    sponsorship_note: str | None = None
    strengths: list[str]
    gaps: list[str]
    missing_requirements: list[str]
    recommendation: str  # APPLY / REVIEW / SKIP
    reason: str
    llm_analysis: LLMJobAnalysis  # kept for transparency / tracker storage


class JobMatchingError(Exception):
    """Raised when the Job Matching Agent can't produce a result at all
    (wraps underlying LLM errors with agent-level context)."""


# ---------------------------------------------------------------------------
# Deterministic scoring functions — pure Python, unit-testable without
# ever calling an LLM. Each takes plain inputs and returns 0-100.
# ---------------------------------------------------------------------------


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_technical_skills(analysis: LLMJobAnalysis) -> int:
    required = len(analysis.required_skills)
    preferred = len(analysis.preferred_skills)
    if required == 0 and preferred == 0:
        return 100  # JD didn't list concrete skills to check against

    required_ratio = (len(analysis.matched_required_skills) / required) if required else 1.0
    preferred_ratio = (len(analysis.matched_preferred_skills) / preferred) if preferred else 1.0
    score = required_ratio * 80 + preferred_ratio * 20
    return round(_clamp(score))


def score_experience(candidate_years: float, min_years_required: float | None) -> int:
    if not min_years_required or min_years_required <= 0:
        return 100
    if candidate_years >= min_years_required:
        return 100
    return round(_clamp((candidate_years / min_years_required) * 100))


_DEGREE_LEVELS = {
    "phd": 4, "doctorate": 4,
    "master": 3, "m.s": 3, "ms ": 3, "m.eng": 3,
    "bachelor": 2, "b.s": 2, "bs ": 2, "b.sc": 2, "b.a": 2,
    "associate": 1,
}


def _degree_level(text: str) -> int:
    text = text.lower()
    return max((level for key, level in _DEGREE_LEVELS.items() if key in text), default=0)


def score_education(resume: MasterResume, education_requirement: str | None) -> int:
    if not education_requirement:
        return 100  # JD didn't specify — nothing to penalize

    required_level = _degree_level(education_requirement)
    if required_level == 0:
        return 100  # couldn't tell what degree level was meant

    candidate_level = max(
        (_degree_level(edu.degree) for edu in resume.education), default=0
    )
    if candidate_level >= required_level:
        return 100
    gap = required_level - candidate_level
    return round(_clamp(100 - gap * 35))


def _seniority_bucket_for_years(years: float) -> str:
    for threshold, bucket in cfg.SENIORITY_YEAR_BUCKETS:
        if years < threshold:
            return bucket
    return cfg.SENIORITY_YEAR_BUCKETS_DEFAULT


def score_seniority(candidate_years: float, job_seniority_level: str) -> int:
    if job_seniority_level not in cfg.SENIORITY_RANK:
        return 100  # NOT_SPECIFIED or an unrecognized value — don't penalize
    candidate_bucket = _seniority_bucket_for_years(candidate_years)
    diff = abs(cfg.SENIORITY_RANK[candidate_bucket] - cfg.SENIORITY_RANK[job_seniority_level])
    return round(_clamp(100 - diff * 25))


def score_location(analysis: LLMJobAnalysis) -> int:
    if analysis.remote_option:
        return 100
    location_text = (analysis.location_text or "").lower()
    if not location_text:
        return 100  # not specified — don't penalize
    if any(keyword in location_text for keyword in cfg.CANDIDATE_REGION_KEYWORDS):
        return 100
    return 50  # explicitly a different, non-remote location


def determine_sponsorship(
    resume: MasterResume, analysis: LLMJobAnalysis
) -> tuple[str, str | None]:
    """
    Returns (compatibility_label, note). Never guesses: only reacts to
    what the LLM found explicitly stated in the job description, and
    always shows your resume's work-authorization wording verbatim.
    """
    if analysis.sponsorship_signal == "NOT_MENTIONED":
        return "UNKNOWN", None

    work_auth = resume.contact.work_authorization or "not specified in your resume"
    quote = analysis.sponsorship_quote or "(no exact quote captured)"

    if analysis.sponsorship_signal == "SPONSORSHIP_AVAILABLE":
        return (
            "COMPATIBLE",
            f'Job states: "{quote}". Your resume states: "{work_auth}".',
        )

    # NO_SPONSORSHIP_STATED
    return (
        "POTENTIAL_CONCERN",
        (
            f'Job states: "{quote}". Your resume states: "{work_auth}". '
            "This is not legal or immigration advice — verify directly with "
            "the employer or an immigration attorney before applying."
        ),
    )


def determine_recommendation(
    overall_score: int, sponsorship_compatibility: str
) -> tuple[str, list[str]]:
    if overall_score >= cfg.APPLY_THRESHOLD:
        recommendation = "APPLY"
    elif overall_score >= cfg.REVIEW_THRESHOLD:
        recommendation = "REVIEW"
    else:
        recommendation = "SKIP"

    notes: list[str] = []
    if sponsorship_compatibility == "POTENTIAL_CONCERN" and recommendation == "APPLY":
        recommendation = "REVIEW"
        notes.append(
            "downgraded from APPLY to REVIEW because the job states a "
            "sponsorship policy that may not match your work authorization"
        )
    return recommendation, notes


def compute_overall_score(sub_scores: dict[str, int]) -> int:
    weighted = sum(sub_scores[dim] * weight for dim, weight in cfg.SCORE_WEIGHTS.items())
    return round(_clamp(weighted))


# ---------------------------------------------------------------------------
# The agent itself.
# ---------------------------------------------------------------------------


class JobMatchingAgent:
    """
    Usage:
        agent = JobMatchingAgent(llm_provider)
        result = agent.evaluate(resume, job_description_text)
    """

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def evaluate(self, resume: MasterResume, job_description_text: str) -> MatchResult:
        from prompts.job_matching_prompts import SYSTEM_PROMPT, build_user_prompt

        try:
            analysis = self._llm.complete_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(resume, job_description_text),
                output_model=LLMJobAnalysis,
            )
        except LLMError as e:
            logger.error("Job Matching Agent: LLM call failed: %s", e)
            raise JobMatchingError(f"Could not analyze this job description: {e}") from e

        candidate_years = parse_total_experience_years(resume)

        sub_scores = {
            "technical_skills": score_technical_skills(analysis),
            "experience": score_experience(candidate_years, analysis.min_years_experience),
            "education": score_education(resume, analysis.education_requirement),
            "seniority": score_seniority(candidate_years, analysis.seniority_level),
            "location": score_location(analysis),
        }
        overall_score = compute_overall_score(sub_scores)

        sponsorship_compatibility, sponsorship_note = determine_sponsorship(resume, analysis)
        recommendation, downgrade_notes = determine_recommendation(
            overall_score, sponsorship_compatibility
        )

        reason = analysis.summary_reason or "No summary reason returned by the LLM."
        if downgrade_notes:
            reason = f"{reason} ({'; '.join(downgrade_notes)})"

        missing_requirements = list(
            dict.fromkeys(  # de-dupe while preserving order
                analysis.missing_required_skills + analysis.other_important_requirements
            )
        )

        result = MatchResult(
            overall_score=overall_score,
            technical_skills_score=sub_scores["technical_skills"],
            experience_score=sub_scores["experience"],
            education_score=sub_scores["education"],
            seniority_score=sub_scores["seniority"],
            location_score=sub_scores["location"],
            sponsorship_compatibility=sponsorship_compatibility,
            sponsorship_note=sponsorship_note,
            strengths=analysis.strengths_notes,
            gaps=analysis.gaps_notes,
            missing_requirements=missing_requirements,
            recommendation=recommendation,
            reason=reason,
            llm_analysis=analysis,
        )

        logger.info(
            "Job match scored | overall=%d | recommendation=%s | technical=%d experience=%d "
            "education=%d seniority=%d location=%d",
            result.overall_score,
            result.recommendation,
            result.technical_skills_score,
            result.experience_score,
            result.education_score,
            result.seniority_score,
            result.location_score,
        )
        return result
