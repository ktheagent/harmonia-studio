import unittest

from harmoonia_studio.playback import PlaybackEvent
from harmonia_studio.playback_workspace import measure_tag, note_tag, parse_measure_value


class PlaybackWorkspaceTests(unittest.TestCase):
    def test_note_tag_matches_notation_preview_identity(self):
        event = PlaybackEvent(0.0, 1.0, 60, 100, 2, 3, 4)
        self.assertEqual(note_tag*event), "note:2:3:4")

    def test_measure_tag(self):
        self.assertEqual(measure_tag(3), "measure:3")
        self.assertEqual(measure_tag(-2), "measure:0")

    def test_parse_measure_value_is_one_based_and_clamped(self):
        self.assertEqual(parse_measure_value("1", 5), 0)
        self.assertEqual(parse_measure_value("5", 5), 4)
        self.assertEqual(parse_measure_value("99", 5), 4)
        self.assertEqual(parse_measure_value("bad", 5), 0)


if __name__ == "__main__":
    unittest.main()
