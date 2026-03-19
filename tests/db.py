# Test the DB schema/constraints (regardless of API/app etc)

import sqlite3
import pytest
from backend.model import init_db


# Create a temporary DB for each test, initialized like the app
@pytest.fixture
def temp_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


########################################################
# TEST 1 - INSERT /items - insert a valid row #
########################################################
def test_insert_valid_row(temp_db):
    conn = sqlite3.connect(temp_db)
    conn.execute(
        "INSERT INTO items (name, category, date_found, location, status, "
        "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
        ("Keys", "electronics", "2026-03-17", "Library", "found", "a@b.co"),
    )
    conn.commit()
    row = conn.execute(
        "SELECT id, name FROM items WHERE name = ?",
        ("Keys",),
    ).fetchone()
    conn.close()
    # Check we get one row back for Keys
    assert row[0] == 1
    assert row[1] == "Keys"


########################################################
# TEST 2 - INSERT /items - insert a row with an empty name #
########################################################
def test_insert_empty_name_raises(temp_db):
    conn = sqlite3.connect(temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO items (name, category, date_found, location, status, "
            "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
            ("   ", "electronics", "2026-03-17", "Library", "found", "a@b.co"),
        )
        conn.commit()
    conn.close()


########################################################
# TEST 3 - INSERT /items - insert a row with a bad date format #
########################################################
def test_insert_bad_date_format_raises(temp_db):
    conn = sqlite3.connect(temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO items (name, category, date_found, location, status, "
            "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "Keys", "electronics", "17/03/2026", "Library",
                "found", "a@b.co",
            ),
        )
        conn.commit()
    conn.close()


########################################################
# TEST 4 - INSERT /items - insert a row with an invalid status #
########################################################
def test_insert_invalid_status_raises(temp_db):
    conn = sqlite3.connect(temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO items (name, category, date_found, location, status, "
            "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "Keys", "electronics", "2026-03-17", "Library",
                "pending", "a@b.co",
            ),
        )
        conn.commit()
    conn.close()


########################################################
# TEST 5 - INSERT /items - insert a row with a null required field #
########################################################
def test_insert_null_required_raises(temp_db):
    conn = sqlite3.connect(temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO items (name, category, date_found, location, status, "
            "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
            (None, "electronics", "2026-03-17", "Library", "found", "a@b.co"),
        )
        conn.commit()
    conn.close()


########################################################
# TEST 6 - INSERT /items - insert a row with a whitespace-only name #
########################################################
def test_insert_whitespace_only_name_raises(temp_db):
    conn = sqlite3.connect(temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO items (name, category, date_found, location, status, "
            "contact_info) VALUES (?, ?, ?, ?, ?, ?)",
            ("   ", "electronics", "2026-03-17", "Library", "found", "a@b.co"),
        )
        conn.commit()
    conn.close()
