"""Controller: user actions → model → refresh view."""

from __future__ import annotations

from backend import model

from frontend.view import MainView


class LostFoundController:
    """Bridges View and Model."""

    def __init__(self, db_path: str, view: MainView) -> None:
        self._db_path = db_path
        self._view = view
        view.set_refresh_handler(self.refresh)

    def refresh(self) -> None:
        """Reload items from the database into the table."""
        rows = model.list_items(self._db_path)
        self._view.set_rows(rows)
