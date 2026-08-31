"""
config/settings.py
-------------------
Central place where the whole app reads its configuration from.

WHY THIS FILE EXISTS:
Every other module (resume loader, LLM client, database, CLI) needs things
like "where is my API key" or "where is my resume file". Instead of each
file calling `os.environ["ANTHROPIC_API_KEY"]` on its own (easy to typo,
hard to see all settings in one place), we define ONE `Settings` class here.
Every other module imports `settings` from this file.

This uses `pydantic-settings`, which does two things for us automatically:
1. Reads values from environment variables (and from a `.env` file, via
   python-dotenv under the hood).
2. Validates types — if ANTHROPIC_API_KEY is missing, you get a clear error
   immediately at startup instead of a confusing crash three modules deep.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The project's root folder (the folder this file's grandparent lives in).
# We compute it so that relative paths (like the resume path) always work
# no matter which directory you run `python main.py` from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # --- LLM provider ---
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-5"
    llm_max_output_tokens: int = 2048
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 3

    # --- App environment ---
    app_env: str = "development"
    log_level: str = "INFO"

    # --- Database ---
    database_url: str = "sqlite:///./database/job_search.db"

    # --- Resume ---
    master_resume_path: str = "resume/master_resume/master_resume.json"

    # --- GitHub (for the Project Importer) ---
    # Both optional: GITHUB_USERNAME lets you skip typing --username every
    # time; GITHUB_TOKEN is only needed if you hit GitHub's unauthenticated
    # rate limit (60 requests/hour) -- a token raises that to 5000/hour.
    # A token here only ever needs "public_repo" read access, never write.
    github_username: str = ""
    github_token: str = ""

    # --- Adzuna (for job discovery / search-jobs) ---
    # Free API -- register at https://developer.adzuna.com/ to get an
    # app_id and app_key (no credit card required for the free tier).
    # We use Adzuna instead of scraping Indeed/Dice/Glassdoor/JobRight
    # directly because Adzuna is an official public API meant for exactly
    # this purpose -- scraping the others would violate their Terms of
    # Service, which this project never does.
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "us"

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unknown env vars instead of crashing
    )

    @property
    def master_resume_full_path(self) -> Path:
        """Resolve MASTER_RESUME_PATH relative to the project root."""
        p = Path(self.master_resume_path)
        return p if p.is_absolute() else PROJECT_ROOT / p


# A single shared instance every module imports:
#   from config.settings import settings
settings = Settings()
