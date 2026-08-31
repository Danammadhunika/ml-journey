"""
prompts/project_import_prompts.py
------------------------------------
The words we send to the LLM to turn one real GitHub repo into a draft
resume Project entry.
"""

import json

SYSTEM_PROMPT = """You write resume "Project" entries from a candidate's
own real GitHub repository data. You are NOT inventing a project -- the
repo, its description, language, topics, and README given to you below
are all real and already belong to the candidate. Your job is only to
summarize and format that real information the way a resume project
entry looks.

HARD RULES (violating any of these makes your answer unsafe to use):
1. Only use facts present in the repo data given to you below (its name,
   description, language, topics, star count, and README text). Never
   invent metrics, users, outcomes, or technologies that aren't evidenced
   there. If the README doesn't mention a number, don't make one up.
2. `name` should be a clean, resume-style project title (you may lightly
   clean up a raw repo name like "movie-rec-app" into "Movie
   Recommendation App," but don't invent a different project).
3. `description` is one sentence summarizing what the project does,
   based only on the description/README given.
4. `bullets` are 2-4 short, resume-style accomplishment lines, each
   traceable to something actually stated in the README or repo data --
   never an invented outcome (e.g. "increased efficiency by 40%") unless
   that exact kind of detail is genuinely in the README.
5. `technologies` should come from the repo's language, topics, and any
   frameworks/libraries explicitly named in the README -- not guessed
   from the project's general subject matter.
6. `claims_referenced` must list every specific, checkable fact you used
   (a technology name, a metric, a feature) as SHORT items, not full
   sentences, so each one can be checked against the repo data afterward.

You must respond only by calling the tool you are given - do not respond
with plain text.
"""


def build_user_prompt(repo: dict, readme_text: str | None) -> str:
    repo_json = json.dumps(
        {
            "name": repo.get("name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "stargazers_count": repo.get("stargazers_count"),
            "html_url": repo.get("html_url"),
        },
        indent=2,
    )
    readme_section = readme_text.strip() if readme_text else "(This repo has no README.)"
    # READMEs can be long -- cap what we send so the request stays small;
    # the first few thousand characters almost always cover what the
    # project is and does.
    readme_section = readme_section[:6000]

    return f"""<REPO_DATA>
{repo_json}
</REPO_DATA>

<REPO_README>
{readme_section}
</REPO_README>

Draft a resume Project entry from this real repo data. Call the tool
with name, description, bullets, technologies, and claims_referenced.
"""
