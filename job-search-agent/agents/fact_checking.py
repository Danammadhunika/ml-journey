"""
agents/fact_checking.py
--------------------------
Shared "does the LLM's claim actually show up in this source text" check,
used by every agent where the LLM has to write original prose instead of
just reordering/scoring your existing content (the GitHub Project
Importer, the Resume/LinkedIn Profile Update Drafter).

WHY THIS IS ITS OWN FILE:
The Recruiter Outreach Agent (agents/recruiter_outreach.py) has its own
version of this same idea, checked against your resume specifically. The
two new agents built alongside this file need the same kind of check but
against DIFFERENT source text (a GitHub repo's real data, or a resume +
a not-yet-added project) -- so the actual word-matching logic lives here
once, and each agent just builds its own "haystack" of true facts to
check against.
"""

from __future__ import annotations

import re


def normalize(text: str) -> str:
    """Lowercase and strip everything except letters, digits, and a few
    characters that matter for numbers/percentages, so "541,909" and
    "541909" or "3.767/4.0 GPA" and "3.767 gpa" compare sensibly.

    Commas are dropped outright (not turned into a space) so a thousands
    separator like "100,000" still merges into the single number "100000"
    rather than splitting into "100" and "000". Everything else that
    isn't a letter/digit/./%/  is turned into a SPACE rather than deleted,
    so "real-time" becomes "real time" -- two separately-matchable words
    -- instead of collapsing into the single unmatchable token
    "realtime"."""
    lowered = text.lower().replace(",", "")
    kept = re.sub(r"[^a-z0-9.%/ ]", " ", lowered)
    return re.sub(r"\s+", " ", kept).strip()


def verify_claims_against_text(
    claims: list[str], source_text: str
) -> tuple[list[str], list[str]]:
    """
    Splits `claims` into (verified, unverified) against `source_text`
    (already-normalized internally). A claim is "verified" if:
      - it appears near-verbatim in the source text, or
      - it contains a number and that exact number appears in the source
        text -- numbers are the most distinctive, hardest-to-fake part of
        a claim, so a number match is trusted even if a generic
        descriptor word around it (like "GPA" or "stars") doesn't itself
        appear anywhere verbatim, or
      - it has no number, and at least half of its significant words
        (ignoring short filler words) show up in the source text.

    Deliberately generous: the goal is to catch clear fabrications, not
    to penalize the LLM for normal, true rephrasing. "Unverified" is a
    signal for a human to double-check, never proof of a lie -- callers
    should always show unverified claims to the user, never silently
    drop or "fix" them.
    """
    haystack = normalize(source_text)
    verified: list[str] = []
    unverified: list[str] = []

    for claim in claims:
        normalized_claim = normalize(claim).strip()
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
