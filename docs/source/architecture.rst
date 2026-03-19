Architecture
============

Overview
--------

This app uses MVC pattern:

- **Model** (`backend.model`): data access, validation, and business rules.
- **View** (`frontend.view`): Tkinter widgets and dialogs only
- **Controller** (`frontend.controller`): handles user actions & bring the view and model together.

This design keeps the 'backend' layer isolated from the user interface, which allows replacing the UI without rewriting the model logic.

Data model
----------

The SQLite table `items` stores:

- id (auto increment primary key)
- name
- category
- date_found (YYYY-MM-DD, nullable)
- date_lost (YYYY-MM-DD, nullable)
- location
- status (found/lost/claimed)
- contact_info

Database constraints and model validation enforce required fields, valid date format, and require at least one of `date_found` or `date_lost`.
