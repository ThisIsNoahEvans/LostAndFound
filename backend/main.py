# SQLite Database over REST API

import sqlite3
import flask

app = flask.Flask(__name__)

# Item class
class Item:
    def __init__(self, item_name: str, category: str, date_found_lost: str, location: str, status: str, contact_info: str):
        self.item_name: str = item_name
        self.category: str = category
        self.date_found_lost: str = date_found_lost
        self.location: str = location
        self.status: str = status
        self.contact_info: str = contact_info

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
@app.route('/items', methods=['GET'])
def get_items() -> tuple[dict, int]:
    conn = sqlite3.connect("lost_and_found.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return flask.jsonify(items), 200



if __name__ == '__main__':
    # Init the db
    init_db()
    app.run(debug=True)