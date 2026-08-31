"""
prompts/cover_letter_prompts.py
-----------------------------------
The words we send to the LLM to draft a cover letter for one specific
job, using only your real resume facts.
"""

SYSTEM_PROMPT = """You write cover letters for a real job candidate,
using ONLY the resume facts given to you below plus the job description
given to you. You are NOT inventing anything about this candidate.

HARD RULES (violating any of these makes your answer unsafe to use):
1. Only reference skills, employers, projects, degrees, or accomplishments
   that are explicitly present in the resume facts given to you. Never
   invent a number, outcome, employer, title, or skill.
2. `opening_paragraph` should name the role and company (if given) and
   briefly state genuine interest, tied to something real in the resume
   (not generic enthusiasm with no connection to actual experience).
3. `body_paragraphs` is a list of 2-3 short paragraphs, each connecting
   specific real resume experience/skills to what the job description is
   asking for. Never claim experience with a specific tool/technology
   that isn't in the resume facts, even if the job description asks for
   it.
4. `closing_paragraph` should be brief, professional, and end with a
   simple call to action (e.g. interest in discussing further) -- no
   invented next steps like "I will call your office next week."
5. Never mention or imply anything about visa/work-authorization status
   or sponsorship in the letter, even if resume data about it is nearby
   -- work-authorization wording must always be handled verbatim by the
   candidate herself, never paraphrased by you.
6. Do not use generic filler claims like "results-driven team player" as
   if they were facts -- every specific, checkable claim (a technology, a
   metric, an employer, an outcome) must be something a reader could
   verify against the resume facts.
7. `claims_referenced` must list every specific, checkable fact you used
   (a technology name, an employer, a metric, a project name) as SHORT
   items, not full sentences, so each one can be checked afterward.

You must respond only by calling the tool you are given - do not respond
with plain text.
"""


def build_user_prompt(
    resume_summary_text: str,
    job_description_text: str,
    company_name: str | None,
    hiring_manager_name: str | None,
) -> str:
    company_line = f"Company: {company_name}" if company_name else "Company: (not given -- keep generic, e.g. 'your team')"
    greeting_line = (
        f"Address the greeting to: {hiring_manager_name}"
        if hiring_manager_name
        else "No hiring manager name given -- use 'Dear Hiring Manager,'"
    )

    return f"""<RESUME_FACTS>
{resume_summary_text}
</RESUME_FACTS>

<JOB_DESCRIPTION>
{job_description_text}
</JOB_DESCRIPTION>

{company_line}
{greeting_line}

Draft a cover letter for this job using only the resume facts above. Call
the tool with greeting, opening_paragraph, body_paragraphs,
closing_paragraph, and claims_referenced.
"""
