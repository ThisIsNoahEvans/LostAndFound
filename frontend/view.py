"""View: Tkinter widgets only. No business logic or SQL."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import Any


class MainView:
    """Main window: form + CRUD buttons + item table."""

    COLUMNS = (
        "id",
        "name",
        "category",
        "date_found",
        "location",
        "status",
        "contact_info",
    )

    STATUS_VALUES = ("found", "lost", "claimed")

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._on_refresh: Callable[[], None] = lambda: None
        self._on_add: Callable[[], None] = lambda: None
        self._on_save: Callable[[], None] = lambda: None
        self._on_delete: Callable[[], None] = lambda: None
        self._on_clear: Callable[[], None] = lambda: None
        self._editing_id: int | None = None

        root.title("Lost & Found")
        root.minsize(880, 520)

        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(main, text="Item details", padding=8)
        form.pack(fill=tk.X, pady=(0, 8))

        self.var_name = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_location = tk.StringVar()
        self.var_status = tk.StringVar(value="found")
        self.var_contact = tk.StringVar()

        

        crud = ttk.Frame(main)
        crud.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(crud, text="Add new", command=self._click_add).pack(
            side=tk.LEFT, padx=(0, 4)
        )

        ttk.Button(crud, text="Refresh list", command=self._click_refresh).pack(
            side=tk.LEFT, padx=(16, 0)
        )

        ttk.Label(main, text="All items").pack(anchor=tk.W)
        tree_frame = ttk.Frame(main)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.COLUMNS,
            show="headings",
            height=10,
        )
        for col in self.COLUMNS:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=95, minwidth=50)
        self.tree.column("id", width=36, minwidth=36)
        scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _click_add(self) -> None:
        self._on_add()

    def _click_save(self) -> None:
        self._on_save()

    def _click_delete(self) -> None:
        self._on_delete()

    def _click_clear(self) -> None:
        self._on_clear()

    def _on_tree_select(self, _event: tk.Event[Any]) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        if values and len(values) >= 7:
            self._load_row(values)

    def _load_row(self, values: tuple[Any, ...]) -> None:
        self._editing_id = int(values[0])
        self.var_name.set(str(values[1]))
        self.var_category.set(str(values[2]))
        self.var_date.set(str(values[3]))
        self.var_location.set(str(values[4]))
        self.var_status.set(str(values[5]).lower())
        self.var_contact.set(str(values[6]))

    def set_refresh_handler(self, handler: Callable[[], None]) -> None:
        self._on_refresh = handler

    def set_add_handler(self, handler: Callable[[], None]) -> None:
        self._on_add = handler

    def set_save_handler(self, handler: Callable[[], None]) -> None:
        self._on_save = handler

    def set_delete_handler(self, handler: Callable[[], None]) -> None:
        self._on_delete = handler

    def set_clear_handler(self, handler: Callable[[], None]) -> None:
        self._on_clear = handler

    def _click_refresh(self) -> None:
        self._on_refresh()

    def get_form_payload(self) -> dict[str, str]:
        """Dict keys match backend.model (API field names)."""
        return {
            "name": self.var_name.get().strip(),
            "category": self.var_category.get().strip(),
            "date_found": self.var_date.get().strip(),
            "location": self.var_location.get().strip(),
            "status": self.var_status.get().strip(),
            "contact_info": self.var_contact.get().strip(),
        }

    def show_create_dialog(self) -> dict[str, str] | None:
        """Open a pop-up form for creating a new item."""
        top = tk.Toplevel(self.root)
        top.title("Add item")
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        vars_map = {
            "name": tk.StringVar(),
            "category": tk.StringVar(),
            "date_found": tk.StringVar(),
            "location": tk.StringVar(),
            "status": tk.StringVar(value="found"),
            "contact_info": tk.StringVar(),
        }

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        labels = [
            ("Name", "name"),
            ("Category", "category"),
            ("Date (YYYY-MM-DD)", "date_found"),
            ("Location", "location"),
            ("Status", "status"),
            ("Contact", "contact_info"),
        ]
        for row, (label, key) in enumerate(labels):
            ttk.Label(frame, text=f"{label}:").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 8), pady=3
            )
            if key == "status":
                combo = ttk.Combobox(
                    frame,
                    textvariable=vars_map[key],
                    values=self.STATUS_VALUES,
                    state="readonly",
                    width=28,
                )
                combo.grid(row=row, column=1, sticky=tk.W, pady=3)
            else:
                ttk.Entry(
                    frame,
                    textvariable=vars_map[key],
                    width=32,
                ).grid(row=row, column=1, sticky=tk.EW, pady=3)
        frame.columnconfigure(1, weight=1)

        result: dict[str, str] | None = None

        def on_create() -> None:
            nonlocal result
            result = {
                "name": vars_map["name"].get().strip(),
                "category": vars_map["category"].get().strip(),
                "date_found": vars_map["date_found"].get().strip(),
                "location": vars_map["location"].get().strip(),
                "status": vars_map["status"].get().strip(),
                "contact_info": vars_map["contact_info"].get().strip(),
            }
            top.destroy()

        btns = ttk.Frame(frame)
        btns.grid(row=len(labels), column=0, columnspan=2, sticky=tk.E, pady=(8, 0))
        ttk.Button(btns, text="Cancel", command=top.destroy).pack(
            side=tk.RIGHT, padx=(4, 0)
        )
        ttk.Button(btns, text="Create", command=on_create).pack(side=tk.RIGHT)

        top.wait_window()
        return result

    def get_editing_id(self) -> int | None:
        return self._editing_id

    def clear_form(self) -> None:
        self._editing_id = None
        self.var_name.set("")
        self.var_category.set("")
        self.var_date.set("")
        self.var_location.set("")
        self.var_status.set("found")
        self.var_contact.set("")
        for iid in self.tree.selection():
            self.tree.selection_remove(iid)

    def delete_target_id(self) -> int | None:
        """Prefer tree selection, else id from last loaded row."""
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            if vals:
                return int(vals[0])
        return self._editing_id

    def set_rows(self, rows: list[tuple[Any, ...]]) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in rows:
            self.tree.insert("", tk.END, values=row)
