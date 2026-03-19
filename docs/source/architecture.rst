Architecture
============

Overview
--------

The system is organised using MVC principles:

- **Model** (`backend.model`): contains all data access, validation, and
  business rules.
- **View** (`frontend.view`): Tkinter widgets and dialogs only, no SQL.
- **Controller** (`frontend.controller`): handles user actions and coordinates
  model/view updates.

This design keeps the persistence layer isolated from the user interface, which
allows replacing the UI without rewriting the model logic.

Data model
----------

The SQLite table `items` stores:

- id (auto increment primary key)
- name
- category
- date_found (YYYY-MM-DD)
- location
- status (found/lost/claimed)
- contact_info

Database constraints and model validation enforce required fields and valid
values.
