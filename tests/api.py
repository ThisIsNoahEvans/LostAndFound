# Integration tests for the REST API & DB
# must be run with a brand new DB.

# import the Flask app - test without running the flask server
from backend.main import app, init_db
import os
import pytest


@pytest.fixture
def clean_db():
    """Fresh DB file + schema before each test that uses this fixture."""
    if os.path.exists("lost_and_found.db"):
        os.remove("lost_and_found.db")
    init_db()


########################################################
# TEST 1 - GET /items - when empty #
########################################################

def test_get_items(clean_db):
    with app.test_client() as client:
        response = client.get('/items')
        # 204 No Content and no response body
        assert response.status_code == 204
        assert response.get_data(as_text=True) == ""


########################################################
# TEST 2 - POST /items - create a new item #
########################################################

def test_create_item(clean_db):
    with app.test_client() as client:
        # Create an example item
        response = client.post('/items', json={
            "name": "Keys",
            "category": "electronics",
            "date_found": "2026-03-17",
            "location": "Exeter",
            "status": "found",
            "contact_info": "1234567890"
        })

        # Check we got a 201 Created
        assert response.status_code == 201

        # Check we got the same item data - plus ID 1 for the first item
        assert response.json == {
            "id": 1,
            "item_name": "Keys",
            "category": "electronics",
            "date_found_lost": "2026-03-17",
            "location": "Exeter",
            "status": "found",
            "contact_info": "1234567890",
        }


########################################################
# TEST 3 - POST /items - create a new item with missing required fields #
########################################################

def test_create_item_missing_required_fields(clean_db):
    with app.test_client() as client:
        
        # This is missing the contact_info field
        response = client.post('/items', json={
            "name": "Keys",
            "category": "electronics",
            "date_found": "2026-03-17",
            "location": "Exeter",
            "status": "found",
        })
        
        # Check we got a 400 Bad Request
        assert response.status_code == 400
        assert response.json == {"error": "Missing required fields"}


########################################################
# TEST 4 - invalid JSON body
########################################################

def test_create_item_invalid_json(clean_db):
    with app.test_client() as client:
        # manually specify content type, else Flask itself will return 415
        response = client.post(
            "/items",
            data="{not valid json",
            content_type="application/json",
        )
        # should return 400 Bad Request
        assert response.status_code == 400


########################################################
# TEST 5 - GET /items/<id> - return an item by id #
########################################################

def test_get_item(clean_db):
    with app.test_client() as client:
        # clean_db wipes the DB each test — create item 1 first
        client.post(
            "/items",
            json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "found",
                "contact_info": "1234567890",
            },
        )
        
        response = client.get("/items/1")
        # should be 200 OK and the same item data
        assert response.status_code == 200
        assert response.json == {
            "id": 1,
            "item_name": "Keys",
            "category": "electronics",
            "date_found_lost": "2026-03-17",
            "location": "Exeter",
            "status": "found",
            "contact_info": "1234567890",
        }
        
        
########################################################
# TEST 6 - GET /items/<id> - item that doesn't exist #
########################################################

def test_get_item_not_found(clean_db):
    with app.test_client() as client:
        response = client.get("/items/1")
        # should be 404 Not Found
        assert response.status_code == 404
        assert response.json == {}
        
        
########################################################
# TEST 7 - PUT /items/<id> - update an item by id #
########################################################

def test_update_item(clean_db):
    with app.test_client() as client:
        # clean_db wipes the DB each test — create item 1 first
        client.post(
            "/items",
            json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "lost",
                "contact_info": "1234567890",
            },
        )
        
        # Update the item to be 'found'
        response = client.put("/items/1", json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "found",
                "contact_info": "1234567890",
            })
        
        # should be 200 OK and the updated item data
        assert response.status_code == 200
        assert response.json == {
            "id": 1,
            "item_name": "Keys",
            "category": "electronics",
            "date_found_lost": "2026-03-17",
            "location": "Exeter",
            "status": "found",
            "contact_info": "1234567890",
        }
        
        
########################################################
# TEST 8 - PUT /items/<id> - update an item with missing required fields #
########################################################

def test_update_item_missing_required_fields(clean_db):
    with app.test_client() as client:
        # clean_db wipes the DB each test — create item 1 first
        client.post(
            "/items",
            json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "lost",
                "contact_info": "1234567890",
            },
        )
        
        # This is missing the contact_info field
        response = client.put("/items/1", json={
            "name": "Keys",
            "category": "electronics",
            "date_found": "2026-03-17",
            "location": "Exeter",
            "status": "lost",
        })
        
        # should be 400 Bad Request
        assert response.status_code == 400
        assert response.json == {"error": "Missing required fields"}
        
        
########################################################
# TEST 9 - PUT /items/<id> - update an item with invalid JSON #
########################################################

def test_update_item_invalid_json(clean_db):
    with app.test_client() as client:
        # clean_db wipes the DB each test — create item 1 first
        client.post(
            "/items",
            json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "lost",
                "contact_info": "1234567890",
            },
        )
        
        # manually specify content type, else Flask itself will return 415
        response = client.put(
            "/items/1",
            data="{not valid json",
            content_type="application/json",
        )
        
        # flask will return a 400 for invaid JSON
        assert response.status_code == 400
     
        
########################################################
# TEST 10 - DELETE /items/<id> - delete an item by id #
########################################################

def test_delete_item(clean_db):
    with app.test_client() as client:
        # clean_db wipes the DB each test — create item 1 first
        client.post(
            "/items",
            json={
                "name": "Keys",
                "category": "electronics",
                "date_found": "2026-03-17",
                "location": "Exeter",
                "status": "lost",
                "contact_info": "1234567890",
            },
        )
        
        response = client.delete("/items/1")
        # should be 204 No Content
        assert response.status_code == 204
        assert response.get_data(as_text=True) == ""


########################################################
# TEST 11 - DELETE /items/<id> - item that doesn't exist #
########################################################

def test_delete_item_not_found(clean_db):
    with app.test_client() as client:
        response = client.delete("/items/1")
        # should be 404 Not Found
        assert response.status_code == 404
        assert response.json == {}