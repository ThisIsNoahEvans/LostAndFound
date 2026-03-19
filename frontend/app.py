"""
Main tkinter desktop app
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# noqa: E402 - ignore the import errors

import tkinter as tk  # noqa: E402

from backend.model import init_db  # noqa: E402

from frontend.config import DATABASE_PATH  # noqa: E402
from frontend.controller import LostFoundController  # noqa: E402
from frontend.view import MainView  # noqa: E402


def main() -> None:
    # init the DB and create the root window
    init_db(DATABASE_PATH)
    root = tk.Tk()
    view = MainView(root)
    # create the controller and refresh the view
    ctrl = LostFoundController(DATABASE_PATH, view)
    ctrl.refresh()
    root.mainloop()


# run the app
if __name__ == "__main__":
    main()
