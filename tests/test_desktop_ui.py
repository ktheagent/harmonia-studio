import unittest

from harmonia_studio.desktop_ui import DesktopTokens, panel_widths, toolbar_command_names
from harmonia_studio.professional_shell_app import ProfessionalShellHarmoniaApp


class DesktopUITests(unittest.TestCase):
    def test_professional_shell_is_top_level_app(self):
        self.assertTrue(callable(ProfessionalShellHarmoniaApp))

    def test_desktop_tokens_preserve_usable_laptop_minimum(self):
        t = DesktopTokens()
        self.assertGreaterEqual(t.min_width, 1000)
        self.assertGreaterEqual(t.min_height, 650)

    def test_toolbar_groups_include_core_commands(self):
        names = set(toolbar_command_names())
        for name in {"New", "Open", "Save", "Undo", "Redo", "Analyze", "Harmonize", "Import", "Export"}:
            self.assertIn(name, names)

    def test_panel_widths_keep_center_dominant(self):
        left, center, right = panel_widths(1366)
        self.assertGreater(center, left)
        self.assertGreater(center, right)


if __name__ == "__main__":
    unittest.main()
