"""
Lost & Found — minimal Tkinter shell.

Run from project root:
    python -m frontend.app
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python frontend/app.py` to find `backend`
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import tkinter as tk  # noqa: E402
from tkinter import ttk  # noqa: E402

from backend.main import init_db  # noqa: E402

from frontend.config import DATABASE_PATH  # noqa: E402
from frontend.services import fetch_all_items  # noqa: E402


class LostFoundApp:
    """Main window: item list + placeholder for forms (you add these)."""

    COLUMNS = (
        "id",
        "name",
        "category",
        "date_found",
        "location",
        "status",
        "contact_info",
    )

    def __init__(self) -> None:
        init_db(DATABASE_PATH)
        self.root = tk.Tk()
        self.root.title("Lost & Found")
        self.root.minsize(800, 400)

        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Items").pack(anchor=tk.W)
        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(btn_row, text="Refresh", command=self.refresh_list).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        # TODO: Add, Update, Delete, Filter buttons here

        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.COLUMNS,
            show="headings",
            height=12,
        )
        for col in self.COLUMNS:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, minwidth=60)
        self.tree.column("id", width=40, minwidth=40)
        scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        hint = (
            "Next: form fields + Add/Edit/Delete + filter (see assignment)."
        )
        ttk.Label(main, text=hint, foreground="gray").pack(
            anchor=tk.W, pady=(8, 0)
        )

        self.refresh_list()

    def refresh_list(self) -> None:
        """Reload rows from the database into the tree."""
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in fetch_all_items(DATABASE_PATH):
            self.tree.insert("", tk.END, values=row)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    LostFoundApp().run()


if __name__ == "__main__":
    main()
