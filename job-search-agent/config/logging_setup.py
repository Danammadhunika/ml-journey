"""
config/logging_setup.py
------------------------
One shared way to get a logger anywhere in the project.

WHY THIS FILE EXISTS:
"Add logging where appropriate" is a requirement, but if every file called
`logging.basicConfig(...)` differently, you'd get duplicated log lines or
inconsistent formatting. This file configures logging ONCE, the first time
anything asks for a logger, and every other module just calls:

    from config.logging_setup import get_logger
    logger = get_logger(__name__)

Logs go to two places at once:
  1. The console (so you see what's happening while running a command).
  2. logs/app.log (an append-only audit trail — useful later for "show me
     everything the agent has done").
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import PROJECT_ROOT, settings

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # RotatingFileHandler keeps the log file from growing forever: once it
    # hits 1 MB it starts a new file and keeps 3 old ones as backups.
    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger configured with this project's console + file handlers."""
    _configure_root_logger()
    return logging.getLogger(name)
