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
