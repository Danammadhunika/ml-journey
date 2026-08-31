"""
prompts/recruiter_outreach_prompts.py
----------------------------------------
The words we send to the LLM for drafting a recruiter outreach message.

WHY THIS ONE IS DIFFERENT FROM THE JOB MATCHER / TAILORING PROMPTS:
Those two agents never let the LLM write a single new word -- they only
ever score or reorder your existing content. An outreach message can't
work that way; it has to be original prose (a greeting, a reason you're
reaching out, a sign-off). So instead of eliminating fabrication risk
structurally, this prompt does two things: it's extremely strict about
only using facts already in the resume, and it requires the model to
separately list every specific factual claim it used (skills, employers,
numbers) in `claims_referenced` -- so Python can independently check each
one against your resume afterward (see agents/recruiter_outreach.py's
`verify_claims`) and flag anything that doesn't check out for YOU to
review before sending anything.
"""

import json

from resume.schema import MasterResume

SYSTEM_PROMPT = """You draft short, professional outreach messages candidates
send to recruiters about a specific job posting. You are NOT sending
anything -- you are only drafting text for the candidate to review, edit,
and send themselves.

HARD RULES (violating any of these makes your answer unsafe to use):
1. The candidate's resume JSON is the ONLY source of truth about what the
   candidate has done. Never invent skills, experience, metrics, degrees,
   certifications, or accomplishments that are not in the resume JSON.
2. Never claim the candidate has already applied, been referred, spoken to
   anyone at the company, or has any relationship with the recruiter or
   company, unless that is explicitly true from context you were given.
3. Never mention, imply, or speculate about visa sponsorship, work
   authorization, or immigration status in the message, even if the job
   description discusses a sponsorship policy. That is a separate,
   sensitive topic the candidate should raise deliberately and directly if
   and when they choose to -- not something to insert into a first-contact
   message.
4. Keep the tone warm, confident, and concise -- 120 to 180 words. This is
   a first message to a stranger, not a cover letter; no long paragraphs.
5. Sign off using the candidate's actual name from the resume JSON. Do not
   invent a signature block, phone number, or contact detail that is not
   already in the resume JSON.
6. `claims_referenced` must list every specific, checkable fact you used
   in the message body (a skill name, a tool, an employer name, a degree,
   a metric or number) as SHORT items, not full sentences -- e.g. "Python",
   "Sacred Heart University", "541,909 transactions" -- one item per fact,
   so each one can be checked against the resume afterward. Do not include
   generic phrases like "strong communicator" that aren't a checkable fact.

You must respond only by calling the tool you are given - do not respond
with plain text.
"""


def build_user_prompt(
    resume: MasterResume,
    job_description_text: str,
    recruiter_name: str | None,
) -> str:
    resume_json = json.dumps(resume.model_dump(mode="json"), indent=2)
    greeting_instruction = (
        f'Address the message to "{recruiter_name}" by name.'
        if recruiter_name
        else "You don't know the recruiter's name -- use a friendly, generic "
        'opener like "Hi there," instead of a placeholder like "[Name]".'
    )

    return f"""<CANDIDATE_RESUME_JSON>
{resume_json}
</CANDIDATE_RESUME_JSON>

<JOB_DESCRIPTION>
{job_description_text.strip()}
</JOB_DESCRIPTION>

Draft a short outreach message from this candidate to a recruiter about
this specific job posting. {greeting_instruction} Pick 2-3 of the
candidate's strongest, most relevant, and TRUE qualifications for this
specific job to mention -- don't try to list everything. Call the tool
with the subject line, the message body, and claims_referenced.
"""
