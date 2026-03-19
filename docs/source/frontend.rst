Frontend
========

The frontend provides the Tkinter user interface and controller wiring.

Responsibilities
----------------

- `frontend.view`: widgets, dialogs, table rendering, form state
- `frontend.controller`: event handling, CRUD calls, filter/search calls
- `frontend.app`: application entry point

The frontend does not directly execute SQL queries; it calls `backend.model`.
