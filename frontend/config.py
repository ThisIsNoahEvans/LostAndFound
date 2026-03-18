"""Paths shared by the frontend."""

from pathlib import Path

# Project root (parent of frontend/)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATABASE_PATH: str = str(PROJECT_ROOT / "lost_and_found.db")
