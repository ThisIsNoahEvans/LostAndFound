"""View: Tkinter widgets only. No business logic or SQL."""

from __future__ import annotations

import datetime as dt
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
        self._on_apply_filters: Callable[[], None] = lambda: None
        self._on_clear_filters: Callable[[], None] = lambda: None
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
        self.var_filter_category = tk.StringVar()
        self.var_filter_status = tk.StringVar()
        self.var_filter_search = tk.StringVar()

        

        crud = ttk.Frame(main)
        crud.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(crud, text="Add new", command=self._click_add).pack(
            side=tk.LEFT, padx=(0, 4)
        )

        ttk.Button(crud, text="Refresh list", command=self._click_refresh).pack(
            side=tk.LEFT, padx=(16, 0)
        )

        filters = ttk.LabelFrame(main, text="Filters", padding=8)
        filters.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(filters, text="Category:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6), pady=2
        )
        ttk.Entry(
            filters, textvariable=self.var_filter_category, width=20
        ).grid(row=0, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        ttk.Label(filters, text="Status:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 6), pady=2
        )
        status_options = ("",) + self.STATUS_VALUES
        ttk.Combobox(
            filters,
            textvariable=self.var_filter_status,
            values=status_options,
            state="readonly",
            width=14,
        ).grid(row=0, column=3, sticky=tk.W, padx=(0, 10), pady=2)
        ttk.Label(filters, text="Search (name/category):").grid(
            row=0, column=4, sticky=tk.W, padx=(0, 6), pady=2
        )
        ttk.Entry(
            filters, textvariable=self.var_filter_search, width=24
        ).grid(row=0, column=5, sticky=tk.W, padx=(0, 10), pady=2)
        ttk.Button(
            filters, text="Apply", command=self._click_apply_filters
        ).grid(row=0, column=6, sticky=tk.W, padx=(0, 4), pady=2)
        ttk.Button(
            filters, text="Clear", command=self._click_clear_filters
        ).grid(row=0, column=7, sticky=tk.W, pady=2)

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

    def set_apply_filters_handler(self, handler: Callable[[], None]) -> None:
        self._on_apply_filters = handler

    def set_clear_filters_handler(self, handler: Callable[[], None]) -> None:
        self._on_clear_filters = handler

    def _click_refresh(self) -> None:
        self._on_refresh()

    def _click_apply_filters(self) -> None:
        self._on_apply_filters()

    def _click_clear_filters(self) -> None:
        self._on_clear_filters()

    def get_filter_values(self) -> tuple[str, str, str]:
        return (
            self.var_filter_category.get().strip(),
            self.var_filter_status.get().strip(),
            self.var_filter_search.get().strip(),
        )

    def clear_filters(self) -> None:
        self.var_filter_category.set("")
        self.var_filter_status.set("")
        self.var_filter_search.set("")

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
            elif key == "date_found":
                date_row = ttk.Frame(frame)
                date_row.grid(row=row, column=1, sticky=tk.EW, pady=3)
                ttk.Entry(
                    date_row,
                    textvariable=vars_map[key],
                    width=24,
                ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Button(
                    date_row,
                    text="Pick...",
                    command=lambda v=vars_map[key]: self._set_date_from_picker(v),
                ).pack(side=tk.LEFT, padx=(4, 0))
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

    def _set_date_from_picker(self, target_var: tk.StringVar) -> None:
        picked = self._open_date_picker(target_var.get().strip())
        if picked is not None:
            target_var.set(picked)

    def _open_date_picker(self, initial_date: str) -> str | None:
        """Simple built-in date picker, returns YYYY-MM-DD or None."""
        top = tk.Toplevel(self.root)
        top.title("Select date")
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        today = dt.date.today()
        default = today
        if initial_date:
            try:
                default = dt.date.fromisoformat(initial_date)
            except ValueError:
                default = today

        y_var = tk.IntVar(value=default.year)
        m_var = tk.IntVar(value=default.month)
        d_var = tk.IntVar(value=default.day)
        result: str | None = None

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Year").grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        ttk.Label(frame, text="Month").grid(row=0, column=1, sticky=tk.W, padx=(0, 6))
        ttk.Label(frame, text="Day").grid(row=0, column=2, sticky=tk.W)

        y_spin = ttk.Spinbox(frame, from_=2000, to=2100, textvariable=y_var, width=8)
        m_spin = ttk.Spinbox(frame, from_=1, to=12, textvariable=m_var, width=6)
        d_spin = ttk.Spinbox(frame, from_=1, to=31, textvariable=d_var, width=6)
        y_spin.grid(row=1, column=0, sticky=tk.W, padx=(0, 6))
        m_spin.grid(row=1, column=1, sticky=tk.W, padx=(0, 6))
        d_spin.grid(row=1, column=2, sticky=tk.W)

        msg = tk.StringVar(value="")
        ttk.Label(frame, textvariable=msg, foreground="red").grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(6, 0)
        )

        def on_ok() -> None:
            nonlocal result
            try:
                picked = dt.date(y_var.get(), m_var.get(), d_var.get())
            except ValueError:
                msg.set("Invalid date")
                return
            result = picked.isoformat()
            top.destroy()

        btns = ttk.Frame(frame)
        btns.grid(row=3, column=0, columnspan=3, sticky=tk.E, pady=(8, 0))
        ttk.Button(btns, text="Cancel", command=top.destroy).pack(
            side=tk.RIGHT, padx=(4, 0)
        )
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT)

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
