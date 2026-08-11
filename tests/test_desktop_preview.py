import unittest

from harmonia_studio.desktop_preview import build_preview_layout
from harmonia_studio.score import Harmony, Lyric, Measure, Note, Part, Pitch, Score


class DesktopPreviewTests(unittest.TestCase):
    def test_layout_contains_selectable_note_harmony_and_lyric(self):
        measure = Measure(
            1,
            notes=[Note(Pitch("C", 4, 1), 1, voice=2, onset=1, lyrics=[Lyric("Sing")])],
            harmonies=[Harmony("C", symbol="Cmaj7")],
        )
        score = Score("Demo", "Composer", [Part("P1", "Voice", measures=[measure])])
        layout = build_preview_layout(score)
        heads = [e for e in layout.elements if e.kind == "ellipse"]
        self.assertEqual(len(heads), 1)
        self.assertIn("score-note", heads[0].tags)
        self.assertIn("note:0:0:0", heads[0].tags)
        self.assertIn("voice:2", heads[0].tags)
        self.assertTrue(any(e.text == "#" for e in layout.elements))
        self.assertTrue(any(e.text == "Cmaj7" for e in layout.elements))
        self.assertTrue(any(e.text == "Sing" for e in layout.elements))

    def test_zoom_changes_dimensions(self):
        score = Score(parts=[Part("P1", "P", measures=[Measure(1)])])
        normal = build_preview_layout(score, zoom=1)
        large = build_preview_layout(score, zoom=2)
        self.assertGreater(large.width, normal.width)
        self.assertGreater(large.height, normal.height)

    def test_note_tags_are_unique_across_parts(self):
        score = Score(parts=[
            Part("P1", "S", measures=[Measure(1, notes=[Note(Pitch("C",5),1)])]),
            Part("P2", "B", measures=[Measure(1, notes=[Note(Pitch("C",3),1)])]),
        ])
        layout = build_preview_layout(score)
        tags = {t for e in layout.elements for t in e.tags if t.startswith("note:")}
        self.assertIn("note:0:0:0", tags)
        self.assertIn("note:1:0:0", tags)

    def test_rest_is_selectable(self):
        score = Score(parts=[Part("P1", "P", measures=[Measure(1, notes=[Note(None, 1, onset=2)])])])
        layout = build_preview_layout(score)
        rests = [e for e in layout.elements if e.kind == "rect" and "score-note" in e.tags]
        self.assertEqual(len(rests), 1)
        self.assertIn("note:0:0:0", rests[0].tags)


if __name__ == "__main__":
    unittest.main()
