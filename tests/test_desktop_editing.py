import unittest
from harmonia_studio.desktop_editing import parse_harmony_symbol, validate_duration

class DesktopEditingValidationTests(unittest.TestCase):
    def test_duration_accepts_positive_finite_value(self):
        self.assertEqual(validate_duration(1.5), 1.5)

    def test_duration_rejects_nonpositive_and_nonfinite(self):
        for value in (0, -1, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                validate_duration(value)

    def test_parse_major_minor_and_slash_harmony(self):
        self.assertEqual(parse_harmony_symbol("Cmaj7").root, "C")
        self.assertEqual(parse_harmony_symbol("Cmaj7").kind, "major-seventh")
        edit = parse_harmony_symbol("F#m7/C#")
        self.assertEqual((edit.root, edit.kind, edit.bass), ("F#", "minor-seventh", "C#"))

    def test_parse_empty_harmony_returns_none(self):
        self.assertIsNone(parse_harmony_symbol("  "))

    def test_parse_rejects_bad_root(self):
        with self.assertRaises(ValueError):
            parse_harmony_symbol("Hmaj7")

if __name__ == "__main__":
    unittest.main()
