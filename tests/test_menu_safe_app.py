import tkinter as tk
import unittest

from harmonia_studio.menu_safe_app import find_menu_entry_by_label


class FakeMenu:
    def __init__(self, entries):
        self.entries = entries

    def index(self, what):
        if what == "end":
            return len(self.entries) - 1 if self.entries else None
        raise AssertionError(what)

    def type(self, index):
        return self.entries[index]["type"]

    def entrycget(self, index, option):
        if option != "label":
            raise AssertionError(option)
        entry = self.entries[index]
        if entry["type"] in {"tearoff", "separator"}:
            raise tk.TclError("unknown option \"-label\"")
        return entry.get("label", "")


class MenuSafetyTests(unittest.TestCase):
    def test_find_label_skips_tearoff_and_separator(self):
        menu = FakeMenu(
            [
                {"type": "tearoff"},
                {"type": "command", "label": "Undo"},
                {"type": "separator"},
                {"type": "command", "label": "Redo"},
            ]
        )
        self.assertEqual(find_menu_entry_by_label(menu, "Undo"), 1)
        self.assertEqual(find_menu_entry_by_label(menu, "Redo"), 3)
        self.assertIsNone(find_menu_entry_by_label(menu, "Missing"))

    def test_empty_menu_returns_none(self):
        self.assertIsNone(find_menu_entry_by_label(FakeMenu([]), "Edit"))


if __name__ == "__main__":
    unittest.main()
