Testing
=======

Test suites
-----------

- `tests/model.py`: integration-style model tests for CRUD and filtering
- `tests/db.py`: database constraint tests (direct SQLite inserts)

Run tests
---------

From project root:

.. code-block:: bash

   pytest tests/model.py tests/db.py -v

Current coverage areas include:

- create/read/update/delete behaviour
- required-field and payload validation
- category/status filters and combined keyword search
- SQLite CHECK/NOT NULL constraints
