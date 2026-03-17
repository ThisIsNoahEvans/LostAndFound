# SQLite Database over REST API

import sqlite3
import flask

app = flask.Flask(__name__)

# Item class
class Item:
    def __init__(self, id: int, item_name: str, category: str, date_found_lost: str, location: str, status: str, contact_info: str):
        self.id: int = id
        self.item_name: str = item_name
        self.category: str = category
        self.date_found_lost: str = date_found_lost
        self.location: str = location
        self.status: str = status
        self.contact_info: str = contact_info
        
    # Return as a dictionary - this could then be used to convert to JSON
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "item_name": self.item_name,
            "category": self.category,
            "date_found_lost": self.date_found_lost,
            "location": self.location,
            "status": self.status,
            "contact_info": self.contact_info
        }

# Init the db if it doesn't exist (first run)
def init_db(db_path: str = "lost_and_found.db") -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                date_found TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                contact_info TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

# GET /items - return all items
# curl http://127.0.0.1:5000/items
@app.route('/items', methods=['GET'])
def get_items() -> tuple[dict, int]:
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    # if none - return 204 (no content)
    if not items:
        return flask.jsonify({}), 204
    return flask.jsonify(items), 200

# POST /items - create a new item
# curl -X POST http://127.0.0.1:5000/items -H "Content-Type: application/json" -d '{"name":"Keys","category":"electronics","date_found":"2026-03-17","location":"Library","status":"Found","contact_info":"student@exeter.ac.uk"}'
@app.route('/items', methods=['POST'])
def create_item() -> tuple[dict, int]:
    data = flask.request.json
    item = Item(None, data['name'], data['category'], data['date_found'], data['location'], data['status'], data['contact_info'])
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, category, date_found, location, status, contact_info) VALUES (?, ?, ?, ?, ?, ?)", (item.item_name, item.category, item.date_found_lost, item.location, item.status, item.contact_info))
    conn.commit()
    new_id = cursor.lastrowid  # ID assigned by the database
    return flask.jsonify({**item.to_dict(), "id": new_id}), 201

# GET /items/<id> - return an item by id
# curl http://127.0.0.1:5000/items/1
@app.route('/items/<int:id>', methods=['GET'])
def get_item(id: int) -> tuple[dict, int]:
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (id,))
    item = cursor.fetchone()
    if not item:
        return flask.jsonify({}), 404
    return flask.jsonify(item), 200

# PUT /items/<id> - update an item by id
# curl -X PUT http://127.0.0.1:5000/items/1 -H "Content-Type: application/json" -d '{"name":"Keys","category":"electronics","date_found":"2026-03-17","location":"Library","status":"Claimed","contact_info":"student@exeter.ac.uk"}'
@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id: int) -> tuple[dict, int]:
    data = flask.request.json
    item = Item(id, data['name'], data['category'], data['date_found'], data['location'], data['status'], data['contact_info'])
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name = ?, category = ?, date_found = ?, location = ?, status = ?, contact_info = ? WHERE id = ?", (item.item_name, item.category, item.date_found_lost, item.location, item.status, item.contact_info, id))
    conn.commit()
    return flask.jsonify(item.to_dict()), 200

# DELETE /items/<id> - delete an item by id
# curl -X DELETE http://127.0.0.1:5000/items/1
@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id: int) -> tuple[dict, int]:
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    return flask.jsonify({}), 204

if __name__ == '__main__':
    # Init the db
    init_db()
    app.run(debug=True)