from __future__ import annotations

import tkinter as tk

from .app import HarmoniaApp
from .persistent_playback_app import PersistentPlaybackHarmoniaApp


LABELED_MENU_TYPES = {"cascade", "command", "checkbutton", "radiobutton"}


def find_menu_entry_by_label(menu, label: str) -> int | None:
    """Return the index of a labeled Tk menu entry without touching tearoffs/separators."""
    end = menu.index("end")
    if end is None:
        return None

    for index in range(int(end) + 1):
        try:
            if menu.type(index) not in LABELED_MENU_TYPES:
                continue
            if menu.entrycget(index, "label") == label:
                return index
        except tk.TclError:
            continue
    return None


class MenuSafeHarmoniaApp(PersistentPlaybackHarmoniaApp):
    """Top-level app layer that avoids Tk tearoff/separator label lookups during startup."""

    def _build_menu(self):
        # The historical EnhancedHarmoniaApp._build_menu looks up "label"
        # on every root/Edit entry. Tk tearoff and separator entries do not
        # support that option on Windows. Build the base menu directly, then
        # rewire Undo/Redo using type-aware lookups.
        HarmoniaApp._build_menu(self)
        menubar = self.nametowidget(self.cget("menu"))

        edit_index = find_menu_entry_by_label(menubar, "Edit")
        if edit_index is None:
            return

        try:
            edit = self.nametowidget(menubar.entrycget(edit_index, "menu"))
        except tk.TclError:
            return

        for label, command in (("Undo", self._undo_edit), ("Redo", self._redo_edit)):
            index = find_menu_entry_by_label(edit, label)
            if index is not None:
                edit.entryconfigure(index, state="normal", command=command)
