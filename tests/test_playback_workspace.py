import unittest
from harmonia_studio.playback import PlaybackEvent
from harmonia_studio.playback_workspace import note_tag, parse_measure_value

class PlaybackWorkspaceTests(unittest.TestCase):
    def test_note_tag(self):
        e = PlaybackEvent(0,1,60,100,2,3,4)
        self.assertEqual(note_tag(e), "note:2:3:4")

    def test_measure_parse(self):
        self.assertEqual(parse_measure_value("1", 5), 0)
        self.assertEqual(parse_measure_value("99", 5), 4)

if __name__ == "__main__":
    unittest.main()
