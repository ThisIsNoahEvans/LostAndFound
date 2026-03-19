Run Guide
=========

Requirements
------------

- Python 3.11+
- Virtual environment recommended

Install
-------

From project root:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

Run desktop application
-----------------------

.. code-block:: bash

   python -m frontend.app

The app creates `lost_and_found.db` on first run.
