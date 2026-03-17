# SQLite Database over REST API

import sqlite3
import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)