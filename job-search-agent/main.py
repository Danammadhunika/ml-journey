"""
main.py
-------
The command-line entry point for the whole project.

WHY THIS FILE EXISTS:
This is the one file you actually run (`python main.py <command>`).
It doesn't contain business logic itself -- it just wires together the
agents/modules built in the other folders. As we add more components
(job matching, resume tailoring, etc.) we'll add more commands here, but
the file stays thin: it should always read like a table of contents.

We use Typer (built by the same author as FastAPI) because it turns a
plain Python function into a CLI command just by adding type hints --
no argparse boilerplate, and it gives us nice --help text for free.
"""

import datetime
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents.cover_letter import CoverLetterAgent, CoverLetterError
from agents.job_matcher import JobMatchingAgent, JobMatchingError, MatchResult
from agents.profile_update import ProfileUpdateAgent, ProfileUpdateError
from agents.project_importer import ProjectImportAgent, ProjectImportError
from agents.recruiter_outreach import RecruiterOutreachAgent, RecruiterOutreachError
from agents.resume_tailoring import ResumeTailoringAgent, ResumeTailoringError
from config.settings import settings
from database.db import get_session, init_db
from database.export_service import export_tracker_to_excel
from database.learning_service import (
    LearningError,
    get_learning_entry,
    list_learning,
    log_learning,
    set_learning_status,
)
from database.models import APPLICATION_STATUSES, LEARNING_STATUSES
from database.tracker_service import (
    TrackerError,
    find_latest_by_company,
    get_application,
    list_applications,
    log_company_update,
    save_match_result,
    update_status,
)
from integrations.github.client import GitHubError, get_readme_text, get_repo, list_public_repos
from integrations.job_sources.adzuna_client import JobBoardError, search_jobs
from integrations.llm import LLMError, get_llm_provider
from resume.loader import (
    ResumeNotFoundError,
    ResumeValidationError,
    load_master_resume,
    save_master_resume,
)
from resume.pdf_export import PdfExportError, text_or_markdown_to_pdf
from resume.render import render_resume_markdown
from resume.schema import Project

app = typer.Typer(help="Personal AI Job Search & Application Agent")
console = Console()


@app.callback()
def _root():
    """
    Personal AI Job Search & Application Agent.

    This empty callback exists so Typer always requires a subcommand name
    (e.g. `validate-resume`) even while this project only has one command.
    Without it, Typer collapses a single-command app into a "no subcommand
    needed" mode, which would break once we add `daily` / `weekly` later.
    """
    # Make sure the tracker's database file/table exist before any command
    # runs. Cheap and idempotent -- does nothing if it's already set up.
    init_db()


@app.command("validate-resume")
def validate_resume():
    """
    Load master_resume.json, validate it against the schema, and print a
    summary. Run this after editing your resume to catch mistakes early --
    every other agent in this project depends on this file being valid.
    """
    try:
        resume = load_master_resume()
    except ResumeNotFoundError as e:
        console.print(f"[bold red]Resume not found:[/bold red]\n{e}")
        raise typer.Exit(code=1)
    except ResumeValidationError as e:
        console.print(f"[bold red]Resume is invalid:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Resume loaded and valid for {resume.contact.name}[/bold green]\n")

    table = Table(title="Master Resume Summary")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", resume.contact.name)
    table.add_row("Location", resume.contact.location or "-")
    table.add_row("Skills tracked", str(len(resume.all_skill_terms())))
    table.add_row("Experience entries", str(len(resume.experience)))
    table.add_row("Education entries", str(len(resume.education)))
    table.add_row("Projects", str(len(resume.projects)))
    table.add_row("Certifications", str(len(resume.certifications)))
    console.print(table)

    top_skills = ", ".join(sorted(resume.all_skill_terms())[:10])
    console.print(f"\n[bold]Sample skills:[/bold] {top_skills}")


@app.command("export-resume-pdf")
def export_resume_pdf_command(
    output: Optional[Path] = typer.Option(
        None, "--output", help="Where to save (default: resume/generated/master_resume.pdf)"
    ),
):
    """
    Export your current master resume as a PDF, exactly as it stands in
    master_resume.json -- no job-specific tailoring. Use this for your
    general resume (LinkedIn, a job board profile, an application that
    doesn't have a specific posting to tailor against). For a resume
    reordered around one specific job, use tailor-resume instead.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    output_path = output or Path("resume/generated/master_resume.pdf")
    try:
        text_or_markdown_to_pdf(render_resume_markdown(resume), output_path, title="Resume")
    except PdfExportError as e:
        console.print(f"[bold red]Could not create PDF:[/bold red] {e}")
        raise typer.Exit(code=1)
    console.print(f"[bold cyan]Resume PDF saved to:[/bold cyan] {output_path}")


def _print_match_result(result: MatchResult) -> None:
    """Shared rendering used by both `match-job` and `show-application`,
    so a saved application looks on screen exactly like it did when you
    first scored it."""
    score_color = "green" if result.overall_score >= 80 else "yellow" if result.overall_score >= 60 else "red"
    console.print(
        f"\n[bold {score_color}]MATCH SCORE: {result.overall_score}/100[/bold {score_color}]  "
        f"[bold]Recommendation: {result.recommendation}[/bold]\n"
    )

    table = Table(title="Score Breakdown")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_row("Technical Skills", f"{result.technical_skills_score}/100")
    table.add_row("Experience", f"{result.experience_score}/100")
    table.add_row("Education", f"{result.education_score}/100")
    table.add_row("Seniority", f"{result.seniority_score}/100")
    table.add_row("Location", f"{result.location_score}/100")
    table.add_row("Sponsorship Compatibility", result.sponsorship_compatibility)
    console.print(table)

    if result.strengths:
        console.print(Panel("\n".join(f"• {s}" for s in result.strengths), title="Strengths", border_style="green"))
    if result.gaps:
        console.print(Panel("\n".join(f"• {g}" for g in result.gaps), title="Gaps", border_style="yellow"))
    if result.missing_requirements:
        console.print(
            Panel(
                "\n".join(f"• {m}" for m in result.missing_requirements),
                title="Important Missing Requirements",
                border_style="red",
            )
        )
    if result.sponsorship_note:
        console.print(Panel(result.sponsorship_note, title="Sponsorship Note", border_style="cyan"))

    console.print(f"\n[bold]Reason:[/bold] {result.reason}")


@app.command("match-job")
def match_job(
    job_description_path: Path = typer.Argument(
        ..., help="Path to a .txt file containing the job description"
    ),
    save: bool = typer.Option(
        False,
        "--save/--no-save",
        help="Also save this result to your Application Tracker database.",
    ),
    title: Optional[str] = typer.Option(
        None, "--title", help="Job title, for the tracker (required with --save)."
    ),
    company: Optional[str] = typer.Option(
        None, "--company", help="Company name, for the tracker (optional)."
    ),
    url: Optional[str] = typer.Option(
        None, "--url", help="Link to the job posting, for the tracker (optional)."
    ),
):
    """
    Score a job description against your master resume: 0-100 overall,
    per-dimension sub-scores, strengths/gaps, sponsorship note, and an
    APPLY / REVIEW / SKIP recommendation.

    This only reads and analyzes — it never applies, emails, or contacts
    anyone. Pass --save (with --title) to also record the result in your
    local Application Tracker database.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not job_description_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {job_description_path}")
        raise typer.Exit(code=1)
    job_description_text = job_description_path.read_text(encoding="utf-8")

    if save and not title:
        console.print("[bold red]--save requires --title \"Some Job Title\"[/bold red]")
        raise typer.Exit(code=1)

    try:
        agent = JobMatchingAgent(llm_provider=get_llm_provider())
        result = agent.evaluate(resume, job_description_text)
    except (LLMError, JobMatchingError) as e:
        console.print(f"[bold red]Could not score this job:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    _print_match_result(result)

    if save:
        with get_session() as session:
            application = save_match_result(
                session,
                job_title=title,
                job_description_text=job_description_text,
                match_result=result,
                company=company,
                source_url=url,
            )
            application_id = application.id
        console.print(
            f"\n[bold cyan]Saved to tracker as application #{application_id} "
            f"(status: NOT_APPLIED).[/bold cyan]"
        )


@app.command("list-applications")
def list_applications_command(
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help=f"Filter by status. One of: {', '.join(APPLICATION_STATUSES)}",
    ),
):
    """
    List every job you've saved to the tracker (newest first), with its
    score, recommendation, and current status.
    """
    try:
        with get_session() as session:
            applications = list_applications(session, status=status)
            # Read every field we need while the session is still open.
            rows = [
                (
                    a.id,
                    a.job_title,
                    a.company or "-",
                    f"{a.overall_score}/100",
                    a.recommendation,
                    a.status,
                    a.created_at.strftime("%Y-%m-%d"),
                )
                for a in applications
            ]
    except TrackerError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    if not rows:
        console.print("No tracked applications yet. Use `match-job --save --title \"...\"` to add one.")
        return

    table = Table(title="Application Tracker")
    table.add_column("ID", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Score", justify="right")
    table.add_column("Recommendation")
    table.add_column("Status")
    table.add_column("Saved On")
    for row in rows:
        table.add_row(*(str(v) for v in row))
    console.print(table)


@app.command("show-application")
def show_application_command(
    application_id: int = typer.Argument(..., help="The tracker ID shown by list-applications."),
):
    """Show the full saved match result for one tracked application."""
    try:
        with get_session() as session:
            application = get_application(session, application_id)
            result = MatchResult(
                overall_score=application.overall_score,
                technical_skills_score=application.technical_skills_score,
                experience_score=application.experience_score,
                education_score=application.education_score,
                seniority_score=application.seniority_score,
                location_score=application.location_score,
                sponsorship_compatibility=application.sponsorship_compatibility,
                sponsorship_note=application.sponsorship_note,
                strengths=json.loads(application.strengths_json),
                gaps=json.loads(application.gaps_json),
                missing_requirements=json.loads(application.missing_requirements_json),
                recommendation=application.recommendation,
                reason=application.reason,
                llm_analysis={"summary_reason": application.reason},
            )
            title, company, status = application.job_title, application.company, application.status
    except TrackerError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]{title}[/bold]" + (f" @ {company}" if company else ""))
    console.print(f"Current status: [bold]{status}[/bold]")
    _print_match_result(result)


@app.command("update-status")
def update_status_command(
    application_id: int = typer.Argument(..., help="The tracker ID shown by list-applications."),
    new_status: str = typer.Argument(
        ..., help=f"New status. One of: {', '.join(APPLICATION_STATUSES)}"
    ),
    notes: Optional[str] = typer.Option(
        None, "--notes", help="Optional note to attach (e.g. 'Recruiter screen scheduled for Tuesday')."
    ),
):
    """
    Update the status of a tracked application, e.g.:
        python main.py update-status 3 APPLIED
        python main.py update-status 3 INTERVIEWING --notes "Phone screen 9/2"

    This is the ONLY way an application's status ever changes — nothing
    in this project marks a job "APPLIED" automatically.
    """
    try:
        with get_session() as session:
            application = update_status(session, application_id, new_status.upper(), notes=notes)
            job_title, status = application.job_title, application.status
    except TrackerError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]#{application_id} ({job_title}) is now {status}.[/bold green]")


@app.command("tailor-resume")
def tailor_resume_command(
    job_description_path: Path = typer.Argument(
        ..., help="Path to a .txt file containing the job description"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the tailored resume as Markdown "
        "(default: resume/generated/tailored_resume.md)",
    ),
    pdf: bool = typer.Option(
        True, "--pdf/--no-pdf", help="Also save a PDF version alongside the Markdown (default: on)."
    ),
):
    """
    Reorder your EXISTING skills and bullets to lead with whatever is most
    relevant to this specific job -- nothing is invented, edited, or
    rewritten. Saves a Markdown copy you can read through and use as a
    reference while updating your real resume by hand.

    This never overwrites your master resume -- master_resume.json is
    never touched by this command.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not job_description_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {job_description_path}")
        raise typer.Exit(code=1)
    job_description_text = job_description_path.read_text(encoding="utf-8")

    try:
        agent = ResumeTailoringAgent(llm_provider=get_llm_provider())
        result = agent.tailor(resume, job_description_text)
    except (LLMError, ResumeTailoringError) as e:
        console.print(f"[bold red]Could not tailor a resume for this job:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    console.print("[bold green]Resume tailored (reordered only -- nothing added or changed).[/bold green]\n")

    if result.required_skills or result.preferred_skills:
        table = Table(title="What This Job Is Looking For")
        table.add_column("Required")
        table.add_column("Preferred")
        rows = max(len(result.required_skills), len(result.preferred_skills))
        for i in range(rows):
            req = result.required_skills[i] if i < len(result.required_skills) else ""
            pref = result.preferred_skills[i] if i < len(result.preferred_skills) else ""
            table.add_row(req, pref)
        console.print(table)

    console.print(
        Panel(
            ", ".join(result.tailored_resume.skills[:12])
            + (" ..." if len(result.tailored_resume.skills) > 12 else ""),
            title="Skills (reordered, most relevant first)",
            border_style="cyan",
        )
    )

    if result.emphasis_notes:
        console.print(
            Panel(
                "\n".join(f"• {n}" for n in result.emphasis_notes),
                title="What's Being Emphasized, and Why",
                border_style="green",
            )
        )

    output_path = output or Path("resume/generated/tailored_resume.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resume_markdown = render_resume_markdown(result.tailored_resume)
    output_path.write_text(resume_markdown, encoding="utf-8")
    console.print(f"\n[bold cyan]Full tailored resume saved to:[/bold cyan] {output_path}")

    if pdf:
        pdf_path = output_path.with_suffix(".pdf")
        try:
            text_or_markdown_to_pdf(resume_markdown, pdf_path, title="Resume")
            console.print(f"[bold cyan]PDF saved to:[/bold cyan] {pdf_path}")
        except PdfExportError as e:
            console.print(f"[bold yellow]Could not create a PDF (Markdown version was still saved):[/bold yellow] {e}")


@app.command("draft-outreach")
def draft_outreach_command(
    job_description_path: Path = typer.Argument(
        ..., help="Path to a .txt file containing the job description"
    ),
    recruiter_name: Optional[str] = typer.Option(
        None, "--recruiter-name", help="Recruiter's first name, if you know it (optional)."
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the draft as text (default: resume/generated/outreach_message.txt)",
    ),
):
    """
    Draft a short outreach message to a recruiter about a specific job.

    IMPORTANT: this only DRAFTS text. This project has no email or
    LinkedIn integration, so nothing is ever sent -- you copy, review,
    edit, and send this yourself. Every specific fact the draft mentions
    is checked against your real resume afterward; anything that can't be
    verified is flagged below so you know exactly what to double-check
    before using it.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not job_description_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {job_description_path}")
        raise typer.Exit(code=1)
    job_description_text = job_description_path.read_text(encoding="utf-8")

    try:
        agent = RecruiterOutreachAgent(llm_provider=get_llm_provider())
        result = agent.draft(resume, job_description_text, recruiter_name=recruiter_name)
    except (LLMError, RecruiterOutreachError) as e:
        console.print(f"[bold red]Could not draft an outreach message:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]Subject:[/bold] {result.subject_line}\n\n{result.message_body}",
            title="Draft Outreach Message (review before sending -- nothing is sent automatically)",
            border_style="cyan",
        )
    )

    if result.verified_claims:
        console.print(
            f"[green]Checked against your resume, these look accurate:[/green] "
            f"{', '.join(result.verified_claims)}"
        )
    if result.unverified_claims:
        console.print(
            Panel(
                "\n".join(f"- {c}" for c in result.unverified_claims),
                title="Could Not Verify Against Your Resume -- Double-Check Before Sending",
                border_style="red",
            )
        )

    output_path = output or Path("resume/generated/outreach_message.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"Subject: {result.subject_line}\n\n{result.message_body}\n", encoding="utf-8"
    )
    console.print(f"\n[bold cyan]Draft saved to:[/bold cyan] {output_path}")


@app.command("import-github-project")
def import_github_project_command(
    repo_name: str = typer.Argument(..., help="The repo's name on GitHub, e.g. 'movie-rec-app'"),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        help="Your GitHub username (defaults to GITHUB_USERNAME in .env, if set).",
    ),
    add_to_resume: bool = typer.Option(
        False,
        "--add-to-resume/--no-add-to-resume",
        help="After drafting, ask (with a yes/no prompt) to append this project to your master resume.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the drafted project as JSON "
        "(default: resume/generated/imported_project_<repo>.json)",
    ),
):
    """
    Turn one of your real public GitHub repos into a draft resume Project
    entry (name, description, bullets, technologies) -- grounded only in
    the repo's actual description/README/language/topics, never invented.

    This only reads from GitHub's public API -- it never pushes, comments,
    or changes anything on GitHub. With --add-to-resume, after you review
    the draft you'll get a yes/no prompt before anything is written to
    your master resume (a backup of the old file is made first).
    """
    github_username = username or settings.github_username
    if not github_username:
        console.print(
            "[bold red]No GitHub username given.[/bold red] Pass --username, "
            "or set GITHUB_USERNAME in your .env."
        )
        raise typer.Exit(code=1)

    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    try:
        repo = get_repo(github_username, repo_name)
        readme_text = get_readme_text(github_username, repo_name)
    except GitHubError as e:
        console.print(f"[bold red]Could not fetch this repo from GitHub:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    try:
        agent = ProjectImportAgent(llm_provider=get_llm_provider())
        result = agent.import_repo(repo, readme_text)
    except (LLMError, ProjectImportError) as e:
        console.print(f"[bold red]Could not draft a project entry:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    project = result.project
    console.print(
        Panel(
            f"[bold]{project.name}[/bold]\n\n{project.description}\n\n"
            + "\n".join(f"- {b}" for b in project.bullets)
            + (f"\n\nTechnologies: {', '.join(project.technologies)}" if project.technologies else ""),
            title="Draft Project Entry (review before adding to your resume)",
            border_style="cyan",
        )
    )

    if result.verified_claims:
        console.print(
            f"[green]Checked against this repo's real data, these look accurate:[/green] "
            f"{', '.join(result.verified_claims)}"
        )
    if result.unverified_claims:
        console.print(
            Panel(
                "\n".join(f"- {c}" for c in result.unverified_claims),
                title="Could Not Verify Against This Repo -- Double-Check Before Using",
                border_style="red",
            )
        )

    output_path = output or Path(f"resume/generated/imported_project_{repo_name}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(project.model_dump(mode="json"), indent=2), encoding="utf-8")
    console.print(f"\n[bold cyan]Draft saved to:[/bold cyan] {output_path}")

    if add_to_resume:
        if result.unverified_claims:
            console.print(
                "[yellow]Heads up: this draft has unverified claims above -- "
                "double-check them before adding to your real resume.[/yellow]"
            )
        if not typer.confirm(f"Add '{project.name}' to your master resume now?"):
            console.print("Not added. Your master resume was not changed.")
            return
        updated_resume = resume.model_copy(deep=True)
        updated_resume.projects.append(project)
        saved_path = save_master_resume(updated_resume)
        console.print(
            f"[bold green]Added '{project.name}' to your master resume.[/bold green] "
            f"(A backup of the previous version was saved to {saved_path}.bak)"
        )


@app.command("draft-profile-update")
def draft_profile_update_command(
    highlight: Optional[str] = typer.Option(
        None,
        "--highlight",
        help="Freeform text describing something new you learned or built.",
    ),
    project_file: Optional[Path] = typer.Option(
        None,
        "--project-file",
        help="Path to a project JSON file saved by import-github-project.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the draft as text (default: resume/generated/profile_update.txt)",
    ),
):
    """
    Draft an updated LinkedIn "About" section plus a short "what's new"
    blurb, from your real resume plus one new highlight -- either
    freeform text (--highlight) or a project JSON file you already
    produced with import-github-project (--project-file). You can pass
    both together.

    IMPORTANT: this only DRAFTS text. This project has no LinkedIn
    integration, so nothing is ever posted or edited on your profile --
    you copy, review, edit, and update LinkedIn yourself. Every specific
    fact the draft mentions is checked against your resume and the
    highlight you gave it; anything that can't be verified is flagged
    below so you know exactly what to double-check before using it.
    """
    if not highlight and not project_file:
        console.print(
            "[bold red]Give me something new to highlight:[/bold red] pass "
            "--highlight \"...\" and/or --project-file path/to/project.json"
        )
        raise typer.Exit(code=1)

    highlight_parts: list[str] = []
    if highlight:
        highlight_parts.append(highlight)

    if project_file:
        if not project_file.exists():
            console.print(f"[bold red]File not found:[/bold red] {project_file}")
            raise typer.Exit(code=1)
        try:
            project = Project.model_validate(json.loads(project_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError) as e:
            console.print(f"[bold red]{project_file} is not a valid project file:[/bold red]\n{e}")
            raise typer.Exit(code=1)
        highlight_parts.append(
            " | ".join(
                p
                for p in [project.name, project.description, *project.bullets, *project.technologies]
                if p
            )
        )

    highlight_text = "\n".join(highlight_parts)

    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    try:
        agent = ProfileUpdateAgent(llm_provider=get_llm_provider())
        result = agent.draft(resume, highlight_text)
    except (LLMError, ProfileUpdateError) as e:
        console.print(f"[bold red]Could not draft a profile update:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            result.linkedin_about,
            title="Draft LinkedIn About Section (review before pasting in -- nothing is posted automatically)",
            border_style="cyan",
        )
    )
    console.print(
        Panel(
            result.whats_new_blurb,
            title="Draft \"What's New\" Blurb",
            border_style="cyan",
        )
    )

    if result.verified_claims:
        console.print(
            f"[green]Checked against your resume and highlight, these look accurate:[/green] "
            f"{', '.join(result.verified_claims)}"
        )
    if result.unverified_claims:
        console.print(
            Panel(
                "\n".join(f"- {c}" for c in result.unverified_claims),
                title="Could Not Verify -- Double-Check Before Using",
                border_style="red",
            )
        )

    output_path = output or Path("resume/generated/profile_update.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"LinkedIn About:\n\n{result.linkedin_about}\n\n"
        f"What's New Blurb:\n\n{result.whats_new_blurb}\n",
        encoding="utf-8",
    )
    console.print(f"\n[bold cyan]Draft saved to:[/bold cyan] {output_path}")


@app.command("list-github-repos")
def list_github_repos_command(
    username: Optional[str] = typer.Option(
        None, "--username", help="Your GitHub username (defaults to GITHUB_USERNAME in .env, if set)."
    ),
    limit: int = typer.Option(20, "--limit", help="Maximum number of repos to show."),
):
    """
    List your real public GitHub repositories (forks excluded), newest-
    pushed first -- so you can see the exact repo names to use with
    import-github-project without having to go check GitHub yourself.

    Read-only: this only lists what's already public on GitHub.
    """
    github_username = username or settings.github_username
    if not github_username:
        console.print(
            "[bold red]No GitHub username given.[/bold red] Pass --username, "
            "or set GITHUB_USERNAME in your .env."
        )
        raise typer.Exit(code=1)

    try:
        repos = list_public_repos(github_username)
    except GitHubError as e:
        console.print(f"[bold red]Could not fetch your repos from GitHub:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not repos:
        console.print(f"No public, non-fork repositories found for '{github_username}'.")
        return

    table = Table(title=f"{github_username}'s Public GitHub Repos")
    table.add_column("Name")
    table.add_column("Language")
    table.add_column("Stars", justify="right")
    table.add_column("Last Pushed")
    for repo in repos[:limit]:
        table.add_row(
            repo.get("name", ""),
            repo.get("language") or "-",
            str(repo.get("stargazers_count", 0)),
            (repo.get("pushed_at") or "")[:10],
        )
    console.print(table)
    console.print(
        "\n[bold cyan]Use the 'Name' column with:[/bold cyan] "
        f"python main.py import-github-project <name> --username {github_username}"
    )


@app.command("search-jobs")
def search_jobs_command(
    query: str = typer.Argument(..., help='What to search for, e.g. "python developer"'),
    location: Optional[str] = typer.Option(None, "--location", help='e.g. "remote" or "New York"'),
    limit: int = typer.Option(10, "--limit", help="Maximum number of results to show."),
    save_description: Optional[int] = typer.Option(
        None,
        "--save-description",
        help="Result number (from the table) to save as a .txt job description file.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the description when using --save-description "
        "(default: resume/generated/job_<n>_description.txt)",
    ),
):
    """
    Search real, live job postings via Adzuna's public job search API.

    We use Adzuna (not Indeed/Dice/Glassdoor/JobRight directly) because it
    offers an official public API meant for exactly this -- scraping
    those other sites would violate their Terms of Service, which this
    project never does. Requires a free ADZUNA_APP_ID / ADZUNA_APP_KEY in
    your .env (sign up at https://developer.adzuna.com/).

    This only searches and displays results -- it never applies to
    anything. Use --save-description to save one result's description as
    a .txt file you can then run through match-job, tailor-resume,
    draft-outreach, or draft-cover-letter.
    """
    try:
        jobs = search_jobs(query, location=location or "", results_per_page=limit)
    except JobBoardError as e:
        console.print(f"[bold red]Could not search jobs:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not jobs:
        console.print("No results found. Try a different query or location.")
        return

    table = Table(title=f"Job Search: \"{query}\"" + (f" in {location}" if location else ""))
    table.add_column("#", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Posted")
    for i, job in enumerate(jobs, start=1):
        table.add_row(
            str(i),
            job["title"],
            job["company"] or "-",
            job["location"] or "-",
            (job["created"] or "")[:10],
        )
    console.print(table)
    console.print(
        "\n[bold cyan]Tip:[/bold cyan] rerun with --save-description <#> to save a job's "
        "description as a .txt file you can feed into match-job, tailor-resume, "
        "draft-outreach, or draft-cover-letter."
    )

    if save_description is not None:
        if save_description < 1 or save_description > len(jobs):
            console.print(f"[bold red]No result #{save_description} in this list.[/bold red]")
            raise typer.Exit(code=1)
        job = jobs[save_description - 1]
        output_path = output or Path(f"resume/generated/job_{save_description}_description.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"{job['title']} at {job['company']}\n"
            f"Location: {job['location']}\n"
            f"Link: {job['redirect_url']}\n\n"
            f"{job['description']}\n"
        )
        output_path.write_text(content, encoding="utf-8")
        console.print(f"[bold green]Saved to:[/bold green] {output_path}")


@app.command("find-jobs")
def find_jobs_command(
    query: str = typer.Argument(..., help='e.g. "python developer"'),
    location: Optional[str] = typer.Option(None, "--location", help='e.g. "New York" or "remote"'),
    limit: int = typer.Option(20, "--limit", help="How many postings to pull and score."),
    threshold: int = typer.Option(
        80,
        "--threshold",
        help="Auto-generate a resume + cover letter (PDFs) + recruiter message for any match "
        "at or above this score (0-100).",
    ),
    save: bool = typer.Option(True, "--save/--no-save", help="Save every scored job to your tracker."),
):
    """
    Search real postings, score EVERY one against your resume, and list
    all of them -- then automatically prepare a tailored resume, cover
    letter (both as PDFs), and a recruiter message for any job scoring
    at or above --threshold (80 by default).

    Every posting is listed regardless of score, so nothing is hidden --
    only strong matches get full materials generated automatically.
    Generating a resume + cover letter + recruiter message for every
    single posting would mean dozens of AI calls and 15-20+ minutes each
    search, so this keeps that to just the jobs worth your time. Lower
    --threshold if you want more jobs to get full materials, or raise it
    if 80+ is still giving you too many.

    This can take a few minutes: scoring alone is one AI call per job
    (so --limit 20 = 20 calls), plus 3 more calls for each job that
    clears the threshold. Progress prints live as it works through the
    list, so you'll see it moving rather than sitting with no output.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    try:
        jobs = search_jobs(query, location=location or "", results_per_page=limit)
    except JobBoardError as e:
        console.print(f"[bold red]Could not search jobs:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not jobs:
        console.print("No results found. Try a different query or location.")
        return

    console.print(f"[bold]Scoring {len(jobs)} postings against your resume (this will take a few minutes)...[/bold]\n")

    llm_provider = get_llm_provider()
    matching_agent = JobMatchingAgent(llm_provider=llm_provider)
    Path("resume/generated").mkdir(parents=True, exist_ok=True)

    summary_rows: list[tuple[int, dict, MatchResult]] = []
    auto_prepared: list[int] = []

    for i, job in enumerate(jobs, start=1):
        job_description_text = (
            f"{job['title']} at {job['company']}\n"
            f"Location: {job['location']}\n"
            f"Link: {job['redirect_url']}\n\n"
            f"{job['description']}\n"
        )
        Path(f"resume/generated/job_{i}_description.txt").write_text(job_description_text, encoding="utf-8")

        try:
            result = matching_agent.evaluate(resume, job_description_text)
        except (LLMError, JobMatchingError) as e:
            console.print(f"  [{i}/{len(jobs)}] [red]Could not score '{job['title']}' @ {job['company']}: {e}[/red]")
            continue

        console.print(
            f"  [{i}/{len(jobs)}] {job['title']} @ {job['company']} ({job['location'] or '-'}) "
            f"-- [bold]{result.overall_score}/100[/bold], {result.recommendation}"
        )
        summary_rows.append((i, job, result))

        resume_pdf_path = cover_letter_pdf_path = recruiter_msg_path = None

        if result.overall_score >= threshold:
            console.print(f"      [cyan]>= {threshold}: preparing resume, cover letter, and recruiter message...[/cyan]")
            try:
                tailor_result = ResumeTailoringAgent(llm_provider=llm_provider).tailor(resume, job_description_text)
                resume_markdown = render_resume_markdown(tailor_result.tailored_resume)
                Path(f"resume/generated/resume_job_{i}.md").write_text(resume_markdown, encoding="utf-8")
                resume_pdf_path = Path(f"resume/generated/resume_job_{i}.pdf")
                text_or_markdown_to_pdf(resume_markdown, resume_pdf_path, title="Resume")
            except (LLMError, ResumeTailoringError, PdfExportError) as e:
                console.print(f"      [yellow]Could not prepare a tailored resume: {e}[/yellow]")

            try:
                cover_result = CoverLetterAgent(llm_provider=llm_provider).draft(
                    resume, job_description_text, company_name=job["company"]
                )
                Path(f"resume/generated/cover_letter_job_{i}.txt").write_text(
                    cover_result.full_text, encoding="utf-8"
                )
                cover_letter_pdf_path = Path(f"resume/generated/cover_letter_job_{i}.pdf")
                text_or_markdown_to_pdf(
                    cover_result.full_text, cover_letter_pdf_path, title=f"Cover Letter - {job['company']}"
                )
                if cover_result.unverified_claims:
                    console.print(
                        f"      [yellow]Cover letter has unverified claims -- review before using: "
                        f"{', '.join(cover_result.unverified_claims)}[/yellow]"
                    )
            except (LLMError, CoverLetterError, PdfExportError) as e:
                console.print(f"      [yellow]Could not prepare a cover letter: {e}[/yellow]")

            try:
                outreach_result = RecruiterOutreachAgent(llm_provider=llm_provider).draft(
                    resume, job_description_text
                )
                recruiter_msg_path = Path(f"resume/generated/recruiter_message_job_{i}.txt")
                recruiter_msg_path.write_text(
                    f"Subject: {outreach_result.subject_line}\n\n{outreach_result.message_body}\n",
                    encoding="utf-8",
                )
            except (LLMError, RecruiterOutreachError) as e:
                console.print(f"      [yellow]Could not prepare a recruiter message: {e}[/yellow]")

            auto_prepared.append(i)

        if save:
            with get_session() as session:
                application = save_match_result(
                    session,
                    job_title=job["title"],
                    job_description_text=job_description_text,
                    match_result=result,
                    company=job["company"],
                    source_url=job["redirect_url"],
                )
                application.job_posting_date = (job.get("created") or "")[:10]
                if resume_pdf_path:
                    application.resume_version_path = str(resume_pdf_path)
                if cover_letter_pdf_path:
                    application.cover_letter_path = str(cover_letter_pdf_path)
                if recruiter_msg_path:
                    application.recruiter_message_path = str(recruiter_msg_path)

    console.print()
    table = Table(title=f'Job Search: "{query}"' + (f" in {location}" if location else ""))
    table.add_column("#", justify="right")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Posted")
    table.add_column("Score", justify="right")
    table.add_column("Materials Ready")
    for i, job, result in summary_rows:
        table.add_row(
            str(i),
            job["title"],
            job["company"] or "-",
            job["location"] or "-",
            (job.get("created") or "")[:10],
            f"{result.overall_score}/100",
            "yes" if i in auto_prepared else "-",
        )
    console.print(table)

    console.print(
        f"\n[bold green]{len(auto_prepared)} of {len(summary_rows)} postings scored >= {threshold} and got a "
        f"full resume + cover letter (PDFs) + recruiter message.[/bold green]"
    )
    console.print(
        "Every posting's description and application link were saved to "
        "resume/generated/job_<#>_description.txt -- open that file for the direct application link."
    )


@app.command("draft-cover-letter")
def draft_cover_letter_command(
    job_description_path: Path = typer.Argument(
        ..., help="Path to a .txt file containing the job description"
    ),
    company: Optional[str] = typer.Option(None, "--company", help="Company name, if you know it."),
    hiring_manager: Optional[str] = typer.Option(
        None, "--hiring-manager", help="Hiring manager's name, if you know it."
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Where to save the draft as text (default: resume/generated/cover_letter.txt)",
    ),
    pdf: bool = typer.Option(
        True, "--pdf/--no-pdf", help="Also save a PDF version alongside the text (default: on)."
    ),
):
    """
    Draft a cover letter for a specific job, using only your real resume
    facts.

    IMPORTANT: this only DRAFTS text. Nothing is ever submitted anywhere
    -- you copy, review, edit, and submit this yourself. Every specific
    fact the draft mentions is checked against your real resume
    afterward; anything that can't be verified is flagged below so you
    know exactly what to double-check before using it.
    """
    try:
        resume = load_master_resume()
    except (ResumeNotFoundError, ResumeValidationError) as e:
        console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    if not job_description_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {job_description_path}")
        raise typer.Exit(code=1)
    job_description_text = job_description_path.read_text(encoding="utf-8")

    try:
        agent = CoverLetterAgent(llm_provider=get_llm_provider())
        result = agent.draft(
            resume, job_description_text, company_name=company, hiring_manager_name=hiring_manager
        )
    except (LLMError, CoverLetterError) as e:
        console.print(f"[bold red]Could not draft a cover letter:[/bold red]\n{e}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            result.full_text,
            title="Draft Cover Letter (review before submitting -- nothing is submitted automatically)",
            border_style="cyan",
        )
    )

    if result.verified_claims:
        console.print(
            f"[green]Checked against your resume, these look accurate:[/green] "
            f"{', '.join(result.verified_claims)}"
        )
    if result.unverified_claims:
        console.print(
            Panel(
                "\n".join(f"- {c}" for c in result.unverified_claims),
                title="Could Not Verify Against Your Resume -- Double-Check Before Using",
                border_style="red",
            )
        )

    output_path = output or Path("resume/generated/cover_letter.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.full_text, encoding="utf-8")
    console.print(f"\n[bold cyan]Draft saved to:[/bold cyan] {output_path}")

    if pdf:
        pdf_path = output_path.with_suffix(".pdf")
        try:
            title = f"Cover Letter - {company}" if company else "Cover Letter"
            text_or_markdown_to_pdf(result.full_text, pdf_path, title=title)
            console.print(f"[bold cyan]PDF saved to:[/bold cyan] {pdf_path}")
        except PdfExportError as e:
            console.print(f"[bold yellow]Could not create a PDF (text version was still saved):[/bold yellow] {e}")


# ---------------------------------------------------------------------------
# Company/opportunity tracking -- added 2026-08-31. These are the commands
# for the ongoing conversation ("I applied", "a recruiter called", "I have
# a screening Tuesday") rather than a fresh match-job scoring run. Every
# one of these looks the company up first (case-insensitive) and updates
# the existing record instead of creating a duplicate -- see
# database/tracker_service.py:log_company_update / find_latest_by_company.
# ---------------------------------------------------------------------------


def _parse_date_option(value: Optional[str], flag_name: str) -> Optional[datetime.datetime]:
    if value is None:
        return None
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        console.print(f"[bold red]{flag_name} must be in YYYY-MM-DD format, got '{value}'.[/bold red]")
        raise typer.Exit(code=1)


@app.command("log-update")
def log_update_command(
    company: str = typer.Argument(..., help='Company name, e.g. "HCL" or "Deloitte".'),
    title: Optional[str] = typer.Option(
        None, "--title", help="Job title (only needed the first time you log this company)."
    ),
    status: Optional[str] = typer.Option(
        None, "--status", help=f"New status. One of: {', '.join(APPLICATION_STATUSES)}"
    ),
    applied_date: Optional[str] = typer.Option(
        None, "--applied-date", help="YYYY-MM-DD (defaults to today when --status APPLIED is used without this)."
    ),
    posting_date: Optional[str] = typer.Option(
        None, "--posting-date", help='When the job was posted, e.g. "2026-08-24".'
    ),
    link: Optional[str] = typer.Option(None, "--link", help="Application link, if you have one."),
    recruiter_contacted: bool = typer.Option(
        False, "--recruiter-contacted", help="Mark that a recruiter reached out (dated today)."
    ),
    recruiter_response: Optional[str] = typer.Option(
        None, "--recruiter-response", help="What the recruiter said."
    ),
    screening: Optional[str] = typer.Option(None, "--screening", help="Screening call notes/status."),
    interview: Optional[str] = typer.Option(None, "--interview", help="Interview notes/status."),
    follow_up: Optional[str] = typer.Option(None, "--follow-up", help="Follow-up date, YYYY-MM-DD."),
    notes: Optional[str] = typer.Option(None, "--notes", help="Any other free-form note."),
):
    """
    Log or update anything about one company's pipeline in a single
    command -- applied, a recruiter call, a screening, an interview, a
    follow-up date, or a status change. Finds the company by name
    (case-insensitive) and updates that EXISTING record; only creates a
    new one the first time this company is mentioned.

    Examples:
        python main.py log-update HCL --status RECRUITER_SCREENING --notes "Screening completed"
        python main.py log-update Deloitte --interview "Waiting on scheduling" --status RESUME_SUBMITTED
        python main.py log-update "Career Guidant Inc" --status APPLIED --applied-date 2026-08-28
    """
    applied_dt = _parse_date_option(applied_date, "--applied-date")
    status_upper = status.upper() if status else None
    if status_upper == "APPLIED" and applied_dt is None:
        applied_dt = datetime.datetime.utcnow()
    follow_up_dt = _parse_date_option(follow_up, "--follow-up")
    recruiter_contacted_dt = datetime.datetime.utcnow() if recruiter_contacted else None

    try:
        with get_session() as session:
            application, created = log_company_update(
                session,
                company,
                job_title=title,
                status=status_upper,
                notes=notes,
                source_url=link,
                job_posting_date=posting_date,
                application_date=applied_dt,
                recruiter_contacted_at=recruiter_contacted_dt,
                recruiter_response=recruiter_response,
                screening_notes=screening,
                interview_notes=interview,
                follow_up_date=follow_up_dt,
            )
            app_id, app_status = application.id, application.status
    except TrackerError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    verb = "Created a new tracker entry" if created else "Updated the existing entry"
    console.print(f"[bold green]{verb} for {company} (#{app_id}) -- status: {app_status}.[/bold green]")


@app.command("show-company")
def show_company_command(
    company: str = typer.Argument(..., help='Company name, e.g. "HCL".'),
):
    """Show the full tracked timeline for one company -- status, recruiter contact, screening, interview, follow-up, notes."""
    with get_session() as session:
        application = find_latest_by_company(session, company)
        if application is None:
            console.print(f"No tracked opportunity for '{company}' yet. Use log-update to add one.")
            return
        data = {
            "company": application.company,
            "job_title": application.job_title,
            "status": application.status,
            "status_updated_at": application.status_updated_at,
            "job_posting_date": application.job_posting_date,
            "application_date": application.application_date,
            "source_url": application.source_url,
            "recruiter_contacted_at": application.recruiter_contacted_at,
            "recruiter_response": application.recruiter_response,
            "screening_notes": application.screening_notes,
            "interview_notes": application.interview_notes,
            "follow_up_date": application.follow_up_date,
            "notes": application.notes,
            "last_activity_at": application.last_activity_at,
        }

    def _fmt(dt):
        return dt.strftime("%Y-%m-%d") if dt else "-"

    lines = [
        f"[bold]Job title:[/bold] {data['job_title']}",
        f"[bold]Status:[/bold] {data['status']} (updated {_fmt(data['status_updated_at'])})",
        f"[bold]Job posted:[/bold] {data['job_posting_date'] or '-'}",
        f"[bold]Applied:[/bold] {_fmt(data['application_date'])}",
        f"[bold]Application link:[/bold] {data['source_url'] or '-'}",
        f"[bold]Recruiter contacted:[/bold] {_fmt(data['recruiter_contacted_at'])}",
        f"[bold]Recruiter response:[/bold] {data['recruiter_response'] or '-'}",
        f"[bold]Screening:[/bold] {data['screening_notes'] or '-'}",
        f"[bold]Interview:[/bold] {data['interview_notes'] or '-'}",
        f"[bold]Follow-up date:[/bold] {_fmt(data['follow_up_date'])}",
        f"[bold]Notes:[/bold] {data['notes'] or '-'}",
        f"[bold]Last activity:[/bold] {_fmt(data['last_activity_at'])}",
    ]
    console.print(Panel("\n".join(lines), title=f"{data['company']} -- Opportunity Timeline", border_style="cyan"))


@app.command("export-tracker")
def export_tracker_command(
    output: Optional[Path] = typer.Option(
        None, "--output", help="Where to save the spreadsheet (default: resume/generated/application_tracker.xlsx)"
    ),
):
    """Export your full Application Tracker as an Excel (.xlsx) spreadsheet -- every column, every tracked company."""
    output_path = output or Path("resume/generated/application_tracker.xlsx")
    with get_session() as session:
        export_tracker_to_excel(session, output_path)
    console.print(f"[bold cyan]Tracker exported to:[/bold cyan] {output_path}")


# ---------------------------------------------------------------------------
# Daily Learning Log -- added 2026-08-31.
# ---------------------------------------------------------------------------


@app.command("log-learning")
def log_learning_command(
    skill: str = typer.Argument(..., help='e.g. "Python" or "FastAPI"'),
    note: Optional[str] = typer.Option(None, "--note", help="Optional detail about what you did."),
):
    """
    Record that you practiced/learned/completed something today. This
    only logs the mention -- it does NOT add anything to your resume.
    See list-learning to review what's been logged, and promote-skill
    when something becomes a genuinely confident skill.
    """
    with get_session() as session:
        entry = log_learning(session, skill, note=note)
        skill_name, count, status = entry.skill, entry.mention_count, entry.status
    console.print(
        f"[bold green]Logged.[/bold green] '{skill_name}' -- mentioned {count} time(s) so far, status: {status}."
    )


@app.command("list-learning")
def list_learning_command(
    status: Optional[str] = typer.Option(
        None, "--status", help=f"Filter by status. One of: {', '.join(LEARNING_STATUSES)}"
    ),
):
    """List everything you've logged learning/practicing, and whether it's made it onto your resume yet."""
    try:
        with get_session() as session:
            entries = list_learning(session, status=status)
            rows = [
                (
                    e.skill,
                    e.status,
                    e.mention_count,
                    "yes" if e.added_to_resume else "no",
                    e.last_mentioned_at.strftime("%Y-%m-%d"),
                )
                for e in entries
            ]
    except LearningError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    if not rows:
        console.print("Nothing logged yet. Use log-learning to add something.")
        return

    table = Table(title="Learning Log")
    table.add_column("Skill")
    table.add_column("Status")
    table.add_column("Mentions", justify="right")
    table.add_column("On Resume")
    table.add_column("Last Mentioned")
    for row in rows:
        table.add_row(*(str(v) for v in row))
    console.print(table)


@app.command("promote-skill")
def promote_skill_command(
    skill: str = typer.Argument(...),
    new_status: str = typer.Argument(..., help=f"One of: {', '.join(LEARNING_STATUSES)}"),
    add_to_resume: bool = typer.Option(
        False, "--add-to-resume", help="Also add this skill to your real master_resume.json skills list."
    ),
):
    """
    Move a skill's status (e.g. LEARNING -> CONFIDENT). This is a
    deliberate call -- never automatic, and never just because a skill
    was mentioned once. Pass --add-to-resume once it's something you'd
    actually claim in an interview; nothing else in this project touches
    master_resume.json.
    """
    try:
        with get_session() as session:
            entry = set_learning_status(session, skill, new_status.upper(), mark_added_to_resume=add_to_resume)
            skill_name, entry_status = entry.skill, entry.status
    except LearningError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]'{skill_name}' is now {entry_status}.[/bold green]")

    if add_to_resume:
        try:
            resume = load_master_resume()
        except (ResumeNotFoundError, ResumeValidationError) as e:
            console.print(f"[bold red]Resume problem:[/bold red]\n{e}")
            raise typer.Exit(code=1)
        if skill_name not in resume.skills:
            resume.skills.append(skill_name)
            save_master_resume(resume)
            console.print(f"[bold cyan]Added '{skill_name}' to master_resume.json skills.[/bold cyan]")
        else:
            console.print(f"'{skill_name}' is already in your resume's skills list.")


if __name__ == "__main__":
    app()
