"""
Data access for the GUI — no Tkinter here.

Extend this module with add_item, update_item, delete_item, search, etc.
"""

from __future__ import annotations

import sqlite3
from typing import Any


def fetch_all_items(db_path: str) -> list[tuple[Any, ...]]:
    """Return all rows from items (id, name, category, date_found, ...)."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT id, name, category, date_found, location, status, "
            "contact_info FROM items ORDER BY id"
        )
        return list(cur.fetchall())
    finally:
        conn.close()
