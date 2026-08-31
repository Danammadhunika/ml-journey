"""
prompts/resume_tailoring_prompts.py
-------------------------------------
The words we send to the LLM for resume tailoring.

WHY THE LLM NEVER TOUCHES BULLET TEXT:
The single biggest risk with an LLM "tailoring" a resume is that it starts
rewriting bullets and quietly slides in a stronger verb, a rounder metric,
or a skill that was never actually there. This project's hard rule is
"never fabricate," so we deliberately never let the LLM generate or edit
bullet/skill text at all. Instead, the LLM's ONLY job is to read the job
description and RATE how relevant each of your EXISTING bullets already
is (0-100). Python then sorts your real, unedited bullets by that score.
The candidate's resume JSON is still the only source of truth; the LLM
is just telling us which true facts to lead with for this specific job.
"""

import json

from resume.schema import MasterResume

SYSTEM_PROMPT = """You are a resume-tailoring analyst. You never write or
rewrite resume content. Your only job is to read a job description and a
candidate's resume, and then:
  1. Extract the job's required and preferred skills.
  2. Score how relevant each of the candidate's EXISTING resume bullets is
     to this specific job description, on a 0-100 scale (100 = directly
     and strongly relevant, 0 = not relevant at all).
  3. Write a few short notes explaining what you're emphasizing and why.

HARD RULES (violating any of these makes your answer unsafe to use):
1. NEVER generate, rewrite, paraphrase, shorten, or "improve" any bullet
   or skill text. You only ever refer to existing bullets by their index
   position -- you never output new bullet text of any kind.
2. The candidate's resume JSON is the ONLY source of truth about what the
   candidate has done. Do not use outside knowledge or "typical" duties
   for someone with this background.
3. Never assume the candidate has a skill just because a related or
   similar skill is present (e.g. Kubernetes does not imply OpenShift).
   Only include a skill in required_skills/preferred_skills if it is an
   accurate reading of the job description itself.
4. `experience_index` is the 0-based position of a job in the resume's
   `experience` array. `bullet_index` is the 0-based position of a bullet
   within that job's `bullets` array. Score every bullet that exists in
   the resume -- do not skip any, and do not invent indexes that don't
   exist in the resume JSON.
5. Every entry in emphasis_notes must be traceable to a specific fact
   already in the resume JSON and a specific requirement in the job
   description. No generic filler, and no claims not backed by the resume.
6. Write emphasis_notes as plain, natural sentences a human would read
   comfortably. NEVER mention "experience_index", "bullet_index", or any
   other internal field/array-position name inside emphasis_notes -- those
   are only for the bullet_relevance list. Refer to bullets and jobs the
   way a person would (e.g. "your current role at Cliff IT Solutions"),
   not by their position number.

You must respond only by calling the tool you are given - do not respond
with plain text.
"""


def build_user_prompt(resume: MasterResume, job_description_text: str) -> str:
    """
    Same pattern as the Job Matching Agent's prompt: the full resume JSON
    (so the model can see exact bullet text and its array positions) plus
    the raw job description, clearly tagged.
    """
    resume_json = json.dumps(resume.model_dump(mode="json"), indent=2)

    return f"""<CANDIDATE_RESUME_JSON>
{resume_json}
</CANDIDATE_RESUME_JSON>

<JOB_DESCRIPTION>
{job_description_text.strip()}
</JOB_DESCRIPTION>

Extract required_skills and preferred_skills from the job description,
score every existing bullet in every experience entry for relevance to
this job (using experience_index / bullet_index positions from the JSON
above), and add a few short emphasis_notes. Call the tool with your
findings. Remember: never output new or edited bullet text.
"""
