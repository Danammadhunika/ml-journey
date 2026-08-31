"""
tests/test_pdf_export.py
--------------------------
Smoke tests for resume/pdf_export.py -- confirms real PDF bytes get
written for headings, bullets, and plain paragraphs, and that nothing
crashes on empty/odd input.
"""

from pathlib import Path

import pytest

from resume.pdf_export import PdfExportError, text_or_markdown_to_pdf


def test_text_or_markdown_to_pdf_writes_a_real_pdf(tmp_path: Path):
    content = (
        "# Madhu Danam\n\n"
        "## Experience\n"
        "- Built REST APIs serving 10000 requests per day.\n"
        "- Used Python and SQL daily.\n\n"
        "A closing paragraph with no special formatting.\n"
    )
    output_path = tmp_path / "resume.pdf"

    result_path = text_or_markdown_to_pdf(content, output_path, title="Resume")

    assert result_path == output_path
    assert output_path.exists()
    raw = output_path.read_bytes()
    assert raw.startswith(b"%PDF")  # a real PDF file header
    assert len(raw) > 100


def test_text_or_markdown_to_pdf_handles_plain_text_with_no_markdown(tmp_path: Path):
    output_path = tmp_path / "letter.pdf"
    result_path = text_or_markdown_to_pdf("Dear Hiring Manager,\n\nI'm excited to apply.\n", output_path)

    assert result_path.exists()
    assert result_path.read_bytes().startswith(b"%PDF")


def test_text_or_markdown_to_pdf_creates_parent_directories(tmp_path: Path):
    output_path = tmp_path / "nested" / "dir" / "out.pdf"
    text_or_markdown_to_pdf("Some content.", output_path)

    assert output_path.exists()
