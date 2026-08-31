"""
resume/pdf_export.py
---------------------
Turns plain text or simple Markdown (the kind tailor-resume, draft-
cover-letter, and draft-outreach already produce) into a clean PDF.

WHY THIS FILE EXISTS:
Madhu asked for the resume and cover letter as PDF documents she can
upload directly to job applications, instead of only .txt/.md files.
This is purely a formatting step -- it takes text that's already been
written and fact-checked elsewhere and lays it out on a page. It never
generates or changes any wording itself.

Supported formatting (deliberately minimal, matches what our Jinja2
resume template and LLM-drafted letters actually produce):
  - "# Heading"   -> large bold heading
  - "## Heading"  -> medium bold heading
  - "- item" / "* item" -> bullet point
  - blank line    -> paragraph spacing
  - everything else -> a normal paragraph
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


class PdfExportError(Exception):
    """Raised when a PDF can't be generated (e.g. write permission problem)."""


def _escape(text: str) -> str:
    # reportlab's Paragraph treats its text as a tiny HTML dialect --
    # escape the characters that would otherwise be interpreted as markup.
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_or_markdown_to_pdf(content: str, output_path: Path, title: str | None = None) -> Path:
    """
    Render `content` (plain text or the light Markdown described above)
    to a PDF at `output_path`. Returns the path for convenience.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], spaceAfter=10)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceAfter=8)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=6)

    story = []
    if title:
        story.append(Paragraph(_escape(title), h1))
        story.append(Spacer(1, 6))

    bullet_buffer: list[str] = []

    def _flush_bullets():
        if bullet_buffer:
            items = [ListItem(Paragraph(_escape(b), body)) for b in bullet_buffer]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 4))
            bullet_buffer.clear()

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            _flush_bullets()
            story.append(Spacer(1, 6))
            continue

        if stripped.startswith("## "):
            _flush_bullets()
            story.append(Paragraph(_escape(stripped[3:]), h2))
        elif stripped.startswith("# "):
            _flush_bullets()
            story.append(Paragraph(_escape(stripped[2:]), h1))
        elif stripped.startswith(("- ", "* ")):
            bullet_buffer.append(stripped[2:])
        else:
            _flush_bullets()
            story.append(Paragraph(_escape(stripped), body))

    _flush_bullets()

    try:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=LETTER,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )
        doc.build(story)
    except Exception as e:  # reportlab raises plain Exception/OSError variants
        raise PdfExportError(f"Could not write PDF to {output_path}: {e}") from e

    return output_path
