"""
resume/loader.py
-----------------
Small utility that reads master_resume.json off disk and turns it into a
validated `MasterResume` object (see resume/schema.py).

WHY THIS FILE EXISTS:
We don't want every part of the app doing its own `open()` + `json.load()`.
Centralizing it here means:
  - One place to give a friendly error if the file is missing.
  - One place to give a friendly error if the JSON doesn't match the schema.
  - Every agent gets the exact same validated object.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from config.settings import settings
from resume.schema import MasterResume


class ResumeNotFoundError(FileNotFoundError):
    """Raised when master_resume.json doesn't exist yet."""


class ResumeValidationError(ValueError):
    """Raised when master_resume.json exists but doesn't match the schema."""


def load_master_resume(path: Path | None = None) -> MasterResume:
    """
    Load and validate the master resume.

    Args:
        path: Optional override. If not given, uses MASTER_RESUME_PATH
              from your .env (via config.settings).

    Returns:
        A validated MasterResume object.

    Raises:
        ResumeNotFoundError: if the JSON file doesn't exist.
        ResumeValidationError: if the JSON file exists but is malformed
                                 or missing required fields.
    """
    resume_path = path or settings.master_resume_full_path

    if not resume_path.exists():
        example_path = resume_path.parent / "master_resume.example.json"
        raise ResumeNotFoundError(
            f"No resume found at: {resume_path}\n"
            f"Copy the template and fill in your real details:\n"
            f"  cp {example_path} {resume_path}\n"
            f"Then edit {resume_path.name} with your real resume content."
        )

    try:
        raw = json.loads(resume_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ResumeValidationError(
            f"{resume_path} is not valid JSON: {e}"
        ) from e

    # Remove any "_README"-style helper keys before validating, so the
    # example file's instructional text doesn't trip up the schema.
    raw.pop("_README", None)

    try:
        return MasterResume.model_validate(raw)
    except ValidationError as e:
        raise ResumeValidationError(
            f"{resume_path} does not match the expected resume format:\n{e}"
        ) from e


def save_master_resume(resume: MasterResume, path: Path | None = None) -> Path:
    """
    Write a MasterResume back to master_resume.json.

    This is used sparingly -- right now, only by the GitHub Project
    Importer's `--add-to-resume` flag, and only after you've explicitly
    confirmed the addition. Two safety steps before anything touches
    disk:
      1. Re-validate the resume object against the schema (catches a
         resume built/edited in memory that doesn't actually satisfy the
         schema's rules, before it can be written).
      2. Back up whatever was already at `path` to `<path>.bak` first --
         this file is the single source of truth for the whole project,
         so overwriting it always leaves you a way back to the previous
         version.
    """
    resume_path = path or settings.master_resume_full_path
    MasterResume.model_validate(resume.model_dump(mode="json"))

    if resume_path.exists():
        backup_path = resume_path.with_suffix(resume_path.suffix + ".bak")
        backup_path.write_text(resume_path.read_text(encoding="utf-8"), encoding="utf-8")

    resume_path.write_text(
        json.dumps(resume.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    return resume_path
