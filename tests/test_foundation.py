import json
import tempfile
import unittest
from pathlib import Path
from harmonia_studio.settings import AppSettings, SettingsService
from harmonia_studio.version import get_version_info
from harmonia_studio.diagnostics import diagnostics
from harmonia_studio.errors import AppError, ErrorCategory

class FoundationTests(unittest.TestCase):
    def test_version(self):
        v = get_version_info()
        self.assertEqual(v.version, "0.9.0")
        self.assertEqual(v.build, 44)

    def test_default_settings(self):
        with tempfile.TemporaryDirectory() as d:
            s = SettingsService(Path(d)/"settings.json")
            self.assertEqual(s.load().theme, "system")

    def test_theme_persists(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"settings.json"
            s = SettingsService(p)
            settings = AppSettings(theme="dark")
            s.save(settings)
            self.assertEqual(s.load().theme, "dark")

    def test_invalid_settings_fall_back(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"settings.json"
            p.write_text('{"schemaVersion": 999, "theme":"broken"}', encoding="utf-8")
            s = SettingsService(p)
            self.assertEqual(s.load().theme, "system")
            self.assertTrue((Path(d)/"settings.json.corrupt").exists())

    def test_diagnostics_has_safe_fields(self):
        d = diagnostics()
        self.assertIn("version", d)
        self.assertIn("architecture", d)
        self.assertIn("settingsSchema", d)

    def test_app_error(self):
        e = AppError("CFG001", ErrorCategory.CONFIGURATION, "Bad config")
        self.assertIn("Bad config", str(e))

if __name__ == "__main__":
    unittest.main()
