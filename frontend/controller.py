"""Controller: user actions → model → refresh view."""

from __future__ import annotations

from tkinter import messagebox

from backend import model

from frontend.view import MainView


class LostFoundController:
    """Bridges View and Model."""

    def __init__(self, db_path: str, view: MainView) -> None:
        self._db_path = db_path
        self._view = view
        view.set_refresh_handler(self.refresh)
        view.set_add_handler(self.add_item)
        view.set_edit_handler(self.edit_item)
        view.set_save_handler(self.save_item)
        view.set_delete_handler(self.delete_item)
        view.set_clear_handler(self.clear_form)
        view.set_apply_filters_handler(self.apply_filters)
        view.set_clear_filters_handler(self.clear_filters)

    def refresh(self) -> None:
        rows = model.list_items(self._db_path)
        self._view.set_rows(rows)

    def apply_filters(self) -> None:
        category, status, keyword = self._view.get_filter_values()
        rows = model.filter_items(
            self._db_path,
            category=category,
            status=status,
            keyword=keyword,
        )
        self._view.set_rows(rows)

    def clear_filters(self) -> None:
        self._view.clear_filters()
        self.refresh()

    def add_item(self) -> None:
        payload = self._view.show_create_dialog()
        if payload is None:
            return
        try:
            model.create_item(self._db_path, payload)
        except ValueError as e:
            messagebox.showerror("Cannot add", str(e), parent=self._view.root)
            return
        self.refresh()

    def edit_item(self) -> None:
        """Edit selected item via separate dialog (double-click or button)."""
        item_id = self._view.get_selected_item_id()
        if item_id is None:
            messagebox.showwarning(
                "No item selected",
                "Select an item in the list first.",
                parent=self._view.root,
            )
            return
        item = model.get_item(self._db_path, item_id)
        if item is None:
            messagebox.showerror(
                "Not found",
                f"No item with id {item_id}.",
                parent=self._view.root,
            )
            self.refresh()
            return
        payload = self._view.show_edit_dialog(
            item_id,
            {
                "name": item.item_name,
                "category": item.category,
                "date_found": item.date_found_lost,
                "location": item.location,
                "status": item.status,
                "contact_info": item.contact_info,
            },
        )
        if payload is None:
            return
        try:
            updated = model.update_item(self._db_path, item_id, payload)
        except ValueError as e:
            messagebox.showerror("Cannot save", str(e), parent=self._view.root)
            return
        if updated is None:
            messagebox.showerror(
                "Not found",
                f"No item with id {item_id}.",
                parent=self._view.root,
            )
        self.refresh()

    def save_item(self) -> None:
        # Kept for backward compatibility; edit now lives in separate dialog.
        self.edit_item()

    def delete_item(self) -> None:
        target = self._view.delete_target_id()
        if target is None:
            messagebox.showwarning(
                "Nothing to delete",
                "Select an item in the list first.",
                parent=self._view.root,
            )
            return
        if not messagebox.askyesno(
            "Confirm delete",
            f"Delete item #{target}? This cannot be undone.",
            parent=self._view.root,
        ):
            return
        if not model.delete_item(self._db_path, target):
            messagebox.showerror(
                "Not found",
                f"Item #{target} no longer exists.",
                parent=self._view.root,
            )
        self.refresh()
        self._view.clear_form()

    def clear_form(self) -> None:
        self._view.clear_form()
