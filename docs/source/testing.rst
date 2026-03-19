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