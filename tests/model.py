# Integration tests for backend.model (MVC model layer; no HTTP).

import os

import pytest

from backend import model

ITEM = {
    "name": "Keys",
    "category": "electronics",
    "date_found": "2026-03-17",
    "location": "Exeter",
    "status": "found",
    "contact_info": "1234567890",
}


@pytest.fixture
def clean_db():
    if os.path.exists(model.DEFAULT_DB_PATH):
        os.remove(model.DEFAULT_DB_PATH)
    model.init_db()


def test_list_items_empty(clean_db):
    assert model.list_items() == []


def test_create_and_get(clean_db):
    created = model.create_item(model.DEFAULT_DB_PATH, dict(ITEM))
    assert created.id == 1
    assert created.to_dict() == {
        "id": 1,
        "item_name": "Keys",
        "category": "electronics",
        "date_found_lost": "2026-03-17",
        "location": "Exeter",
        "status": "found",
        "contact_info": "1234567890",
    }
    rows = model.list_items()
    assert len(rows) == 1
    got = model.get_item(model.DEFAULT_DB_PATH, 1)
    assert got is not None
    assert got.to_dict() == created.to_dict()


def test_create_missing_required_fields(clean_db):
    bad = {k: v for k, v in ITEM.items() if k != "contact_info"}
    with pytest.raises(ValueError, match="Missing required fields"):
        model.create_item(model.DEFAULT_DB_PATH, bad)


def test_create_invalid_payload_type(clean_db):
    with pytest.raises(ValueError, match="JSON body required"):
        model.create_item(model.DEFAULT_DB_PATH, None)
    with pytest.raises(ValueError, match="JSON body required"):
        model.create_item(model.DEFAULT_DB_PATH, "not a dict")


def test_get_item_not_found(clean_db):
    assert model.get_item(model.DEFAULT_DB_PATH, 1) is None


def test_update_item(clean_db):
    model.create_item(model.DEFAULT_DB_PATH, dict(ITEM, status="lost"))
    updated = model.update_item(
        model.DEFAULT_DB_PATH,
        1,
        dict(ITEM, status="found"),
    )
    assert updated is not None
    assert updated.status == "found"


def test_update_missing_fields(clean_db):
    model.create_item(model.DEFAULT_DB_PATH, dict(ITEM))
    with pytest.raises(ValueError, match="Missing required fields"):
        model.update_item(
            model.DEFAULT_DB_PATH,
            1,
            {"name": "X"},
        )


def test_update_item_not_found(clean_db):
    assert model.update_item(model.DEFAULT_DB_PATH, 99, dict(ITEM)) is None


def test_delete_item(clean_db):
    model.create_item(model.DEFAULT_DB_PATH, dict(ITEM))
    assert model.delete_item(model.DEFAULT_DB_PATH, 1) is True
    assert model.get_item(model.DEFAULT_DB_PATH, 1) is None


def test_delete_item_not_found(clean_db):
    assert model.delete_item(model.DEFAULT_DB_PATH, 1) is False


def _seed_filter_items() -> None:
    model.create_item(
        model.DEFAULT_DB_PATH,
        dict(
            ITEM,
            name="Laptop",
            category="electronics",
            status="found",
        ),
    )
    model.create_item(
        model.DEFAULT_DB_PATH,
        dict(
            ITEM,
            name="Jacket",
            category="clothing",
            status="lost",
        ),
    )
    model.create_item(
        model.DEFAULT_DB_PATH,
        dict(
            ITEM,
            name="Chemistry Book",
            category="books",
            status="claimed",
        ),
    )
    model.create_item(
        model.DEFAULT_DB_PATH,
        dict(
            ITEM,
            name="Headphones",
            category="electronics",
            status="lost",
        ),
    )


def test_filter_items_no_filters_returns_all(clean_db):
    _seed_filter_items()
    rows = model.filter_items(model.DEFAULT_DB_PATH)
    assert [row[1] for row in rows] == [
        "Laptop",
        "Jacket",
        "Chemistry Book",
        "Headphones",
    ]


def test_filter_items_category_only(clean_db):
    _seed_filter_items()
    rows = model.filter_items(model.DEFAULT_DB_PATH, category="electronics")
    assert [row[1] for row in rows] == ["Laptop", "Headphones"]


def test_filter_items_status_only(clean_db):
    _seed_filter_items()
    rows = model.filter_items(model.DEFAULT_DB_PATH, status="lost")
    assert [row[1] for row in rows] == ["Jacket", "Headphones"]


def test_filter_items_keyword_matches_name_and_category(clean_db):
    _seed_filter_items()
    name_match = model.filter_items(model.DEFAULT_DB_PATH, keyword="book")
    assert [row[1] for row in name_match] == ["Chemistry Book"]

    category_match = model.filter_items(model.DEFAULT_DB_PATH, keyword="elect")
    assert [row[1] for row in category_match] == ["Laptop", "Headphones"]


def test_filter_items_combined_filters_with_and(clean_db):
    _seed_filter_items()
    rows = model.filter_items(
        model.DEFAULT_DB_PATH,
        category="electronics",
        status="lost",
        keyword="head",
    )
    assert [row[1] for row in rows] == ["Headphones"]


def test_filter_items_case_insensitive_and_whitespace(clean_db):
    _seed_filter_items()
    rows = model.filter_items(
        model.DEFAULT_DB_PATH,
        category="  ELECTRONICS  ",
        status="  LoSt ",
        keyword="  HEAD  ",
    )
    assert [row[1] for row in rows] == ["Headphones"]
