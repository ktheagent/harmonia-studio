import unittest
from harmonia_studio.score import *
from harmonia_studio.notation import render_score_svg, RenderOptions

class NotationTests(unittest.TestCase):
    def test_svg_contains_staff_note_chord_lyric(self):
        m=Measure(1,notes=[Note(Pitch("C",4),1,onset=0,lyrics=[Lyric("Sing")])],
                  harmonies=[Harmony("C",symbol="Cmaj7")])
        s=Score("Demo","Composer",[Part("P1","Voice",measures=[m])])
        svg=render_score_svg(s)
        self.assertIn("<svg",svg)
        self.assertGreaterEqual(svg.count("<line"),6)
        self.assertIn("<ellipse",svg)
        self.assertIn("Cmaj7",svg)
        self.assertIn("Sing",svg)
        self.assertIn("Demo",svg)
    def test_zoom_changes_size(self):
        s=Score(parts=[Part("P1","P",measures=[Measure(1)])])
        a=render_score_svg(s,RenderOptions(zoom=1.0))
        b=render_score_svg(s,RenderOptions(zoom=2.0))
        self.assertNotEqual(a.splitlines()[0],b.splitlines()[0])
