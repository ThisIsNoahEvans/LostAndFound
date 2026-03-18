"""View: Tkinter widgets only. No business logic or SQL."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Any


class MainView:
    """Main window layout + item table."""

    COLUMNS = (
        "id",
        "name",
        "category",
        "date_found",
        "location",
        "status",
        "contact_info",
    )

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._on_refresh: Callable[[], None] = lambda: None

        root.title("Lost & Found")
        root.minsize(800, 400)

        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main, text="Items").pack(anchor=tk.W)
        btn_row = ttk.Frame(main)
        btn_row.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(btn_row, text="Refresh", command=self._click_refresh).pack(
            side=tk.LEFT, padx=(0, 4)
        )

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


    def set_refresh_handler(self, handler: Callable[[], None]) -> None:
        """Controller registers what runs when Refresh is clicked."""
        self._on_refresh = handler

    def _click_refresh(self) -> None:
        self._on_refresh()

    def set_rows(self, rows: list[tuple[Any, ...]]) -> None:
        """Display DB rows in the tree."""
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in rows:
            self.tree.insert("", tk.END, values=row)
