"""Controller - controls the user actions in the tk app"""

from __future__ import annotations
from tkinter import messagebox
from backend import model
from frontend.view import MainView


# the controller class to connect the view and data model
class LostFoundController:
    # init the controller
    def __init__(self, db_path: str, view: MainView) -> None:
        self._db_path = db_path  # path to the DB
        self._view = view  # the view to display the data
        # set the event handlers for the buttons
        view.set_refresh_handler(self.refresh)
        view.set_add_handler(self.add_item)
        view.set_edit_handler(self.edit_item)
        view.set_save_handler(self.save_item)
        view.set_delete_handler(self.delete_item)
        view.set_clear_handler(self.clear_form)
        view.set_apply_filters_handler(self.apply_filters)
        view.set_clear_filters_handler(self.clear_filters)

    # refresh the view with the data from the DB
    def refresh(self) -> None:
        # get the data from the DB
        rows = model.list_items(self._db_path)
        self._view.set_rows(rows)

    # apply the filters to the data
    def apply_filters(self) -> None:
        category, status, keyword = self._view.get_filter_values()
        rows = model.filter_items(
            self._db_path,
            category=category,
            status=status,
            keyword=keyword,
        )
        self._view.set_rows(rows)

    # clear the filters
    def clear_filters(self) -> None:
        self._view.clear_filters()
        self.refresh()

    # add a new item to the DB
    def add_item(self) -> None:
        # show the create dialog
        payload = self._view.show_create_dialog()
        # if the user cancels, return
        if payload is None:
            return
        try:
            model.create_item(self._db_path, payload)
        except ValueError as e:
            messagebox.showerror("Cannot add", str(e), parent=self._view.root)
            return
        self.refresh()

    # edit an existing item
    def edit_item(self) -> None:
        """Edit selected item via separate dialog (double-click or button)."""
        item_id = self._view.get_selected_item_id()
        # make sure an item is selected
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
                "date_found": item.date_found or "",
                "date_lost": item.date_lost or "",
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

    # delete an existing item
    def delete_item(self) -> None:
        # make sure an item is selected
        target = self._view.delete_target_id()
        if target is None:
            # show a warning if no item is selected
            messagebox.showwarning(
                "Nothing to delete",
                "Select an item in the list first.",
                parent=self._view.root,
            )
            return
        # ask the user for confirmation
        if not messagebox.askyesno(
            "Confirm delete",
            f"Delete item #{target}? This cannot be undone.",
            parent=self._view.root,
        ):
            return
        # delete the item from the DB
        if not model.delete_item(self._db_path, target):
            messagebox.showerror(
                "Not found",
                f"Item #{target} no longer exists.",
                parent=self._view.root,
            )
        self.refresh()
        self._view.clear_form()

    # clear the form
    def clear_form(self) -> None:
        self._view.clear_form()
