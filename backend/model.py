"""Backend model for db access"""

from __future__ import annotations

import sqlite3
from typing import Any

DEFAULT_DB_PATH: str = "lost_and_found.db"

REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "category",
    "location",
    "status",
    "contact_info",
)


# type of an Item in the db
class Item:

    def __init__(
        self,
        item_id: int | None,  # autoincrememnt by the DB
        item_name: str,
        category: str,
        date_found: str | None,  # YYYY-MM-DD
        date_lost: str | None,  # YYYY-MM-DD
        location: str,
        status: str,  # found, lost, claimed
        contact_info: str,
    ) -> None:
        self.id: int | None = item_id
        self.item_name: str = item_name
        self.category: str = category
        self.date_found: str | None = date_found
        self.date_lost: str | None = date_lost
        self.location: str = location
        self.status: str = status
        self.contact_info: str = contact_info

    def to_dict(self) -> dict[str, Any]:
        # return the item as a dict
        data: dict[str, Any] = {
            "item_name": self.item_name,
            "category": self.category,
            "date_found": self.date_found,
            "date_lost": self.date_lost,
            "location": self.location,
            "status": self.status,
            "contact_info": self.contact_info,
        }
        if self.id is not None:
            data["id"] = self.id
        return data


# create the table if it doesn't exist
def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                category TEXT NOT NULL CHECK(length(trim(category)) > 0),
                date_found TEXT CHECK(
                    date_found IS NULL OR (
                        date_found GLOB
                            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                        AND date(date_found) IS NOT NULL
                    )
                ),
                date_lost TEXT CHECK(
                    date_lost IS NULL OR (
                        date_lost GLOB
                            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
                        AND date(date_lost) IS NOT NULL
                    )
                ),
                location TEXT NOT NULL CHECK(length(trim(location)) > 0),
                status TEXT NOT NULL CHECK(
                    lower(status) IN ('found', 'lost', 'claimed')
                ),
                contact_info TEXT NOT NULL
                    CHECK(length(trim(contact_info)) > 0),
                CHECK(date_found IS NOT NULL OR date_lost IS NOT NULL)
            )
            """
        )
        conn.commit()
    except Exception as e:
        raise ValueError("Failed to create table") from e
    finally:
        conn.close()


def _clean_optional_date(value: Any) -> str | None:
    """Return None for blank dates, else stripped date string."""
    v = str(value or "").strip()
    return v if v else None


# make sure the data coming in is valid - JSON, right fields, etc
def _validate_payload(data: Any) -> dict[str, Any]:
    if data is None or not isinstance(data, dict):
        raise ValueError("JSON body required")
    if any(not str(data.get(k, "")).strip() for k in REQUIRED_FIELDS):
        raise ValueError("Missing required fields")
    date_found = _clean_optional_date(data.get("date_found"))
    date_lost = _clean_optional_date(data.get("date_lost"))
    if not date_found and not date_lost:
        raise ValueError("Provide date_found or date_lost")
    return data


# convert a row from the DB to an Item type
def _row_to_item(row: tuple[Any, ...]) -> Item:
    return Item(
        int(row[0]),
        str(row[1]),
        str(row[2]),
        str(row[3]) if row[3] is not None else None,
        str(row[4]) if row[4] is not None else None,
        str(row[5]),
        str(row[6]),
        str(row[7]),
    )


# return all items in the DB in a list
def list_items(db_path: str | None = None) -> list[tuple[Any, ...]]:
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items ORDER BY id")
        return list(cur.fetchall())
    finally:
        conn.close()


def distinct_categories(db_path: str | None = None) -> list[str]:
    """Return sorted unique non-empty categories from items table."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT DISTINCT category FROM items "
            "WHERE trim(category) <> '' "
            "ORDER BY lower(category)"
        )
        return [str(row[0]) for row in cur.fetchall()]
    finally:
        conn.close()


# filter the items in the DB by category, status, and keyword
def filter_items(
    db_path: str = DEFAULT_DB_PATH,
    category: str = "",
    status: str = "",
    keyword: str = "",
) -> list[tuple[Any, ...]]:
    clauses: list[str] = []
    params: list[str] = []
    cat = category.strip()  # category to filter by
    stat = status.strip()  # status to filter by
    term = keyword.strip()  # keyword to filter by

    # build query by each filter if it's provided
    if cat:
        clauses.append("lower(category) = lower(?)")
        params.append(cat)
    if stat:
        clauses.append("lower(status) = lower(?)")
        params.append(stat)
    if term:
        clauses.append(
            "(lower(name) LIKE lower(?) OR lower(category) LIKE lower(?))"
        )
        like = f"%{term}%"
        params.extend([like, like])

    # base query - select everythihng
    query = "SELECT * FROM items"
    # if there are any filters, add them
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"

    # execute the query and return the results
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(query, tuple(params))
        return list(cur.fetchall())
    finally:
        conn.close()


# get a specific item by ID
def get_item(db_path: str, item_id: int) -> Item | None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        return _row_to_item(row) if row else None
    finally:
        conn.close()


# create a new item
def create_item(db_path: str, data: Any) -> Item:
    # check the data is valid
    d = _validate_payload(data)
    # create the item object
    item = Item(
        None,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        _clean_optional_date(d.get("date_found")),
        _clean_optional_date(d.get("date_lost")),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )
    conn = sqlite3.connect(db_path)
    try:
        # try to insert the item into the DB
        try:
            cur = conn.execute(
                "INSERT INTO items (name, category, date_found, date_lost, "
                "location, status, contact_info) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    item.item_name,
                    item.category,
                    item.date_found,
                    item.date_lost,
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


# update an existing item
def update_item(db_path: str, item_id: int, data: Any) -> Item | None:
    # check the data is valid
    d = _validate_payload(data)

    # check the item exists
    if get_item(db_path, item_id) is None:
        return None

    item = Item(
        item_id,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        _clean_optional_date(d.get("date_found")),
        _clean_optional_date(d.get("date_lost")),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )

    # update the item in the DB
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE items SET name = ?, category = ?, date_found = ?, "
            "date_lost = ?, location = ?, status = ?, contact_info = ? "
            "WHERE id = ?",
            (
                item.item_name,
                item.category,
                item.date_found,
                item.date_lost,
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


# delete an item from database
def delete_item(db_path: str, item_id: int) -> bool:
    # check the item exists first
    if get_item(db_path, item_id) is None:
        return False

    # delete the item from the DB
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
