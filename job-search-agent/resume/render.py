"""
resume/render.py
-----------------
Turns a MasterResume object into a plain Markdown document using the
Jinja2 template in resume/templates/. Used by the Resume Tailoring Agent's
CLI command to give you something readable to look at and copy from.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from resume.schema import MasterResume

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    # autoescape off on purpose: we're generating Markdown/plain text, not
    # HTML, so we don't want "&" turning into "&amp;" etc.
    autoescape=select_autoescape(enabled_extensions=(), default=False),
    # trim_blocks/lstrip_blocks deliberately left off: the template below
    # controls its own whitespace explicitly with {%- ... -%} where it
    # matters, which is more predictable than the global auto-trim rules
    # once a template mixes single-line and multi-line {% if %} blocks.
)


def render_resume_markdown(resume: MasterResume) -> str:
    template = _env.get_template("tailored_resume.md.j2")
    return template.render(resume=resume)
