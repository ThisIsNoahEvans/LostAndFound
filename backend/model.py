# Backend model to handle database


from __future__ import annotations

import sqlite3
from typing import Any

# path of the default db (current dir)
DEFAULT_DB_PATH: str = "lost_and_found.db"


# required fields for an item
REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "category",
    "date_found",
    "location",
    "status",
    "contact_info",
)


# an individual item record
class Item:

    def __init__(
        self,
        item_id: int | None,  # id of the item (auto increment by db)
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

    # return the item data as a dictionary (to be used for JSON etc)
    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "item_name": self.item_name,
            "category": self.category,
            "date_found_lost": self.date_found_lost,
            "location": self.location,
            "status": self.status,
            "contact_info": self.contact_info,
        }
        # if we have an ID, add it to the dictionary
        if self.id is not None:
            d["id"] = self.id
        return d


# create the items table if it doesn't exist
def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        # create the table with the required fields
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

    # something went wrong!
    except Exception as e:
        raise ValueError("Failed to create table") from e

    # close after we've done everything
    finally:
        conn.close()


def _validate_payload(data: Any) -> dict[str, Any]:
    if data is None or not isinstance(data, dict):
        raise ValueError("JSON body required")
    if any(not str(data.get(k, "")).strip() for k in REQUIRED_FIELDS):
        raise ValueError("Missing required fields")
    return data


# convert a row from the database to an Item object
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


# get all rows from the items table and return them as a list of tuples
def list_items(db_path: str = DEFAULT_DB_PATH) -> list[tuple[Any, ...]]:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items ORDER BY id")
        return list(cur.fetchall())
    finally:
        conn.close()


# filter the items by category, status and keyword
def filter_items(
    db_path: str = DEFAULT_DB_PATH,
    category: str = "",
    status: str = "",
    keyword: str = "",
) -> list[tuple[Any, ...]]:
    # build the SQL query to filter the items
    clauses: list[str] = []
    params: list[str] = []

    cat = category.strip()  # category to filter by
    stat = status.strip()  # status to filter by
    term = keyword.strip()  # keyword to filter by

    if cat:  # if a category is provided, add the clause to the query
        clauses.append("lower(category) = lower(?)")
        params.append(cat)
    if stat:  # if a status is provided, add the clause to the query
        clauses.append("lower(status) = lower(?)")
        params.append(stat)
    if term:  # if a keyword is provided, add the clause to the query
        clauses.append(
            "(lower(name) LIKE lower(?) OR lower(category) LIKE lower(?))"
        )
        like = f"%{term}%"
        params.extend([like, like])

    # start with base (select all) and build up filters as needed
    query = "SELECT * FROM items"  # start with the base query
    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    # always order by ID
    query += " ORDER BY id"

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(query, tuple(params))
        return list(cur.fetchall())
    finally:
        conn.close()


# get an individual item by ID
def get_item(
    db_path: str,
    item_id: int,
) -> Item | None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        # convert it to an Item object
        return _row_to_item(row) if row else None
    finally:
        conn.close()


# create a new item in the DB
def create_item(
    db_path: str,
    data: Any,
) -> Item:
    # check we have all the data we need
    d = _validate_payload(data)

    # create it as an Item
    item = Item(
        None,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        str(d["date_found"]).strip(),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )

    # insert into DB
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
        # something went wrong (doesn't match field constrtaints)
        # revert and error
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError("Data breaks database rules") from e
    finally:
        conn.close()
    item.id = new_id
    return item


# update an item in the DB
def update_item(
    db_path: str,
    item_id: int,
    data: Any,
) -> Item | None:
    # check we have all the data we need
    d = _validate_payload(data)

    # check the item exists
    if get_item(db_path, item_id) is None:
        # no item found, return None
        return None

    # create all the new updated data as an Item
    item = Item(
        item_id,
        str(d["name"]).strip(),
        str(d["category"]).strip(),
        str(d["date_found"]).strip(),
        str(d["location"]).strip(),
        str(d["status"]).strip(),
        str(d["contact_info"]).strip(),
    )

    # update the item in the DB
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
    # something went wrong (doesn't match field constrtaints)
    except sqlite3.IntegrityError as e:
        # don't rollback as nothing was changed
        raise ValueError("Data breaks database rules") from e
    finally:
        conn.close()
    return item


# delete an item from the DB
def delete_item(db_path: str, item_id: int) -> bool:
    if get_item(db_path, item_id) is None:
        # no item found, return False
        return False

    # delete the item from the DB
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        # return True if a row was deleted, False otherwise
        return cur.rowcount > 0
    finally:
        conn.close()
