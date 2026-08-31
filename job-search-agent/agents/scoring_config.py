"""
agents/scoring_config.py
--------------------------
The weights and thresholds behind the Job Matching Agent's 0-100 score,
kept in one file, in plain numbers, so you can see and tune the scoring
logic without hunting through agent code.

WHY THESE WEIGHTS:
+--------------------+--------+---------------------------------------------+
| Dimension          | Weight | Reasoning                                    |
+--------------------+--------+---------------------------------------------+
| Technical skills   |  35%   | The single strongest predictor of getting an |
|                    |        | interview for these roles — most ATS/recruiter|
|                    |        | screens filter on keyword/skill overlap first.|
| Experience (years) |  25%   | Real signal, but softer than skills: many    |
|                    |        | postings list years as a "nice to have" and  |
|                    |        | strong skills can offset a small gap.        |
| Education          |  15%   | Often a checkbox ("Bachelor's or equivalent  |
|                    |        | experience") rather than a hard filter —     |
|                    |        | important when explicit, low-stakes otherwise.|
| Seniority          |  15%   | Filters out obvious mismatches (new-grad vs. |
|                    |        | staff-level) without dominating the score.   |
| Location           |  10%   | Least important: remote work and relocation  |
|                    |        | flexibility mean it rarely disqualifies you  |
|                    |        | outright, but it's still worth flagging.     |
+--------------------+--------+---------------------------------------------+
Sponsorship compatibility is NOT part of the weighted score. It's a
categorical, potentially legally-sensitive flag (COMPATIBLE /
POTENTIAL_CONCERN / UNKNOWN) shown separately, because blending it into a
single number would hide a "STOP AND THINK" signal inside an otherwise
average-looking score.

These are starting values — if you find the agent consistently over- or
under-rating jobs you know are good/bad fits, adjust the numbers here.
"""

# Must sum to 1.0 — enforced by a test in tests/test_job_matcher.py.
SCORE_WEIGHTS = {
    "technical_skills": 0.35,
    "experience": 0.25,
    "education": 0.15,
    "seniority": 0.15,
    "location": 0.10,
}

# Recommendation thresholds, applied to the final weighted overall_score.
APPLY_THRESHOLD = 80  # >= this -> APPLY
REVIEW_THRESHOLD = 60  # >= this (but < APPLY_THRESHOLD) -> REVIEW
# below REVIEW_THRESHOLD -> SKIP

# Seniority level -> numeric rank, used to compare "how senior is this
# candidate" (derived from years of experience) against "how senior is
# this job" (extracted from the JD by the LLM).
SENIORITY_RANK = {
    "ENTRY": 0,
    "JUNIOR": 1,
    "MID": 2,
    "SENIOR": 3,
    "STAFF_OR_ABOVE": 4,
}

# Years-of-experience -> seniority bucket, used only to translate the
# candidate's computed years into the same scale as SENIORITY_RANK above.
SENIORITY_YEAR_BUCKETS = [
    (1.0, "ENTRY"),
    (3.0, "JUNIOR"),
    (5.0, "MID"),
    (8.0, "SENIOR"),
]
SENIORITY_YEAR_BUCKETS_DEFAULT = "STAFF_OR_ABOVE"

# Keywords used for the deterministic location check: if the job's stated
# location text contains any of these (case-insensitive), it's treated as
# within the candidate's target region. Sourced directly from what the
# candidate's own resume states (contact.location + the regions named in
# their summary) — not invented.
CANDIDATE_REGION_KEYWORDS = [
    "connecticut",
    "ct",
    "new york",
    "ny",
    "new jersey",
    "nj",
    "boston",
    "massachusetts",
    "ma",
]
