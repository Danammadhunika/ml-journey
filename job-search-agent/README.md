# Personal AI Job Search & Application Agent

A modular, multi-agent Python project that helps Madhu find, evaluate, and apply
to jobs faster — while keeping a human in the loop for every external action
(submitting applications, sending emails/LinkedIn messages).

**Ground rule the whole system is built around:** the agents never invent
experience. Every resume, cover letter, or outreach message they produce is
built only from what's written in `resume/master_resume/master_resume.json`.

## Status: v1 (MVP) — in progress

Built so far:
- [x] Project scaffolding, config, dependency management
- [x] Master resume data model + validated loader (`resume/schema.py`, `resume/loader.py`)
- [x] LLM integration layer (Anthropic, swappable provider interface)
- [x] Job Matching Agent (0–100 scoring, transparent weighted breakdown)
- [ ] Resume Tailoring Agent
- [ ] Cover Letter Agent
- [ ] Recruiter Outreach Agent
- [ ] Application Tracker (SQLite)
- [ ] `main.py` daily workflow + human approval gate

See the full roadmap (v1 → v4) in the project brief at the bottom of this file.

## Project layout

```
job_search_agent/
├── agents/                 # One file per "brain" (matching, tailoring, etc.)
├── integrations/
│   ├── llm/                 # Swappable LLM provider (Anthropic today)
│   ├── email/                # v2: recruiter email monitoring
│   ├── calendar/              # v3: availability checks
│   └── job_sources/            # v2: job discovery connectors
├── resume/
│   ├── schema.py              # Pydantic models = the "shape" of a resume
│   ├── loader.py               # Reads + validates master_resume.json
│   ├── master_resume/
│   │   ├── master_resume.example.json   # Template — safe to look at, not real
│   │   └── master_resume.json            # YOUR real resume (gitignored)
│   └── generated/               # Tailored resumes get written here (gitignored)
├── database/                  # SQLAlchemy models + the application tracker
├── prompts/                    # LLM prompt templates, kept out of Python code
├── tests/                        # pytest tests
├── config/settings.py            # All configuration in one place
├── logs/                           # Action log (append-only audit trail)
├── .env.example                    # Copy to .env and fill in your API key
├── .gitignore
├── requirements.txt
└── main.py                          # CLI entry point: `python main.py <command>`
```

## Setup (do this once)

```bash
cd job_search_agent

# 1. Create a virtual environment (keeps this project's packages separate
#    from anything else on your machine)
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your secrets
cp .env.example .env
# open .env in an editor and paste in your real ANTHROPIC_API_KEY

# 4. Set up your resume
cp resume/master_resume/master_resume.example.json resume/master_resume/master_resume.json
# open master_resume.json and replace EVERY "REPLACE_..." value with your
# real, truthful resume content. Nothing downstream is allowed to add more
# than what you put here.
```

## Commands available today

```bash
python main.py validate-resume
```
Loads `master_resume.json`, checks it against the schema, and prints a
summary table. Run this any time you edit your resume.

```bash
python main.py match-job path/to/job_description.txt
```
Scores a job description against your resume: overall 0–100 score, a
per-dimension breakdown (technical skills / experience / education /
seniority / location), sponsorship compatibility, strengths, gaps, and an
APPLY / REVIEW / SKIP recommendation. Try it against the bundled example:
```bash
python main.py match-job tests/fixtures/sample_job_description.txt
```
This only reads and analyzes — it never applies to anything or contacts anyone.

## Running the tests

```bash
pytest
```
You should see all tests pass (`5 passed`). These tests check that:
- A well-formed resume loads correctly.
- A resume missing a required field (like email) is rejected, not silently
  accepted with bad data.
- Friendly errors are raised when the resume file is missing or not valid JSON.

## Troubleshooting

**`ModuleNotFoundError: No module named 'pydantic_settings'` (or similar)**
You haven't installed dependencies in this environment yet, or you're not in
the virtual environment. Run `source .venv/bin/activate` then
`pip install -r requirements.txt` again.

**`email-validator is not installed`**
`pip install "pydantic[email]"` (already listed in requirements.txt — rerun
`pip install -r requirements.txt`).

**`Resume not found` when running `validate-resume`**
You haven't copied the example file yet. Run the "Set up your resume" step
above. This file is intentionally excluded from git (see `.gitignore`) so you
never accidentally commit your personal data.

**`Resume is invalid: ... validation error ...`**
Pydantic will tell you exactly which field is wrong (e.g. missing `email`,
or `email` isn't a valid email format). Fix that field in
`master_resume.json` and rerun `python main.py validate-resume`.

**I changed a file and nothing seems to happen**
Make sure your virtual environment is activated (you should see `(.venv)` at
the start of your terminal prompt) and that you're running commands from
inside the `job_search_agent/` folder.

**`No ANTHROPIC_API_KEY found` when running `match-job`**
Your `.env` doesn't have a real key yet. Copy `.env.example` to `.env` and
paste in your key from https://console.anthropic.com/.

**`Anthropic API key rejected` / 401 error**
Your key is invalid, expired, or was copied with extra whitespace. Get a
fresh one from the Anthropic console and update `.env`.

**`Could not score this job` with a rate-limit or timeout message**
The app already retries these automatically (with backoff) up to
`LLM_MAX_RETRIES` times (default 3). If you still see this, wait a minute
and try again, or raise `LLM_MAX_RETRIES`/`LLM_TIMEOUT_SECONDS` in `.env`.

**`LLM output did not match ... after retrying`**
Rare — means Claude's structured answer didn't match the expected schema
twice in a row. Check `logs/app.log` for the validation error detail; if it
keeps happening on the same job description, that JD's phrasing may be
worth simplifying (very long/unusual formatting can sometimes trip this up).

## Security notes

- `.env` (your real API key) is in `.gitignore` — it will never be committed.
- `master_resume.json` (your real resume) is also gitignored — only the
  `.example.json` template is meant to be shared/committed.
- No password is ever stored in this project. The only secret is your
  Anthropic API key, read from an environment variable via `.env`.
- Nothing in this project sends an email, submits an application, or posts
  anywhere on your behalf without an explicit approval step (added in later
  versions of this project).

## Roadmap

- **v1 (current):** resume + job description input → matching/scoring →
  tailored resume → cover letter → recruiter email draft → application
  tracker → human approval. No browser automation, no live job scraping.
- **v2:** job discovery (APIs/permitted sources), email integration,
  recruiter email classification, draft replies.
- **v3:** calendar integration, approved application submission, dashboard,
  scheduled daily/weekly workflows.
- **v4:** advanced agent skills, MCP integrations, deeper automation,
  analytics.
