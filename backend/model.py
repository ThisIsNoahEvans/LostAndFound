"""
Model: domain + persistence. No Tkinter.

Used by the Tkinter Controller. A future web UI could call the same functions.
"""

from __future__ import annotations

import sqlite3
from typing import Any


DEFAULT_DB_PATH: str = "lost_and_found.db"

REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "category",
    "date_found",
    "location",
    "status",
    "contact_info",
)


class Item:
    """One lost/found record."""

    def __init__(
        self,
        item_id: int | None,
        item_name: str,
        category: str,
        date_found_lost: str,
        location: str,
        status: str,
        contact_info: str,
    ) -> None:
        self.id: int | None = item_id
        self.item_name: str = item_name
        self.category: str = category
        self.date_found_lost: str = date_found_lost
        self.location: str = location
        self.status: str = status
        self.contact_info: str = contact_info

    def to_dict(self) -> dict[str, Any]:
        """Shape suitable for JSON API and UI layers."""
        d: dict[str, Any] = {
            "item_name": self.item_name,
            "category": self.category,
            "date_found_lost": self.date_found_lost,
            "location": self.location,
            "status": self.status,
            "contact_info": self.contact_info,
        }
        if self.id is not None:
            d["id"] = self.id
        return d


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Create items table if missing (CHECK constraints match assignment)."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                category TEXT NOT NULL CHECK(length(trim(category)) > 0),
                date_found TEXT NOT NULL CHECK(
                    date_found GLOB
                        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                    AND date(date_found) IS NOT NULL
                ),
                location TEXT NOT NULL CHECK(length(trim(location)) > 0),
                status TEXT NOT NULL CHECK(
                    lower(status) IN ('found', 'lost', 'claimed')
                ),
                contact_info TEXT NOT NULL
                    CHECK(length(trim(contact_info)) > 0)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _validate_payload(data: Any) -> dict[str, Any]:
    if data is None or not isinstance(data, dict):
        raise ValueError("JSON body required")
    if any(not str(data.get(k, "")).strip() for k in REQUIRED_FIELDS):
        raise ValueError("Missing required fields")
    return data


def _row_to_item(row: tuple[Any, ...]) -> Item:
    return Item(
        int(row[0]),
        str(row[1]),
        str(row[2]),
        str(row[3]),
        str(row[4]),
        str(row[5]),
        str(row[6]),
    )


def list_items(db_path: str = DEFAULT_DB_PATH) -> list[tuple[Any, ...]]:
    """All rows as SQLite tuples (API list view)."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items ORDER BY id")
        return list(cur.fetchall())
    finally:
        conn.close()


def get_item(
    db_path: str,
    item_id: int,
) -> Item | None:
    """Return item or None if missing."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        return _row_to_item(row) if row else None
    finally:
        conn.close()


def create_item(
    db_path: str,
    data: Any,
) -> Item:
    """Insert from API-shaped dict (name, date_found, ...). Raises ValueError."""
    d = _validate_payload(data)
    item = Item(
        None,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        str(d["date_found"]).strip(),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )
    conn = sqlite3.connect(db_path)
    try:
        try:
            cur = conn.execute(
                "INSERT INTO items (name, category, date_found, location, "
                "status, contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item.item_name,
                    item.category,
                    item.date_found_lost,
                    item.location,
                    item.status,
                    item.contact_info,
                ),
            )
            conn.commit()
            new_id = int(cur.lastrowid)
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError("Data breaks database rules") from e
    finally:
        conn.close()
    item.id = new_id
    return item


def update_item(
    db_path: str,
    item_id: int,
    data: Any,
) -> Item | None:
    """Update by id. None if id does not exist."""
    d = _validate_payload(data)
    if get_item(db_path, item_id) is None:
        return None
    item = Item(
        item_id,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        str(d["date_found"]).strip(),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE items SET name = ?, category = ?, date_found = ?, "
            "location = ?, status = ?, contact_info = ? WHERE id = ?",
            (
                item.item_name,
                item.category,
                item.date_found_lost,
                item.location,
                item.status,
                item.contact_info,
                item_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError("Data breaks database rules") from e
    finally:
        conn.close()
    return item


def delete_item(db_path: str, item_id: int) -> bool:
    """True if a row was deleted."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
