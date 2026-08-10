import unittest
from harmonia_studio.score import *
from harmonia_studio.arrangement.engine import auto_arrange
from harmonia_studio.arrangement.templates import get_template

class ArrangementTests(unittest.TestCase):
    def sample(self):
        ms=[Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)]) for i,p in enumerate([72,74,71,72])]
        return Score("Tune","",[Part("P1","Melody",measures=ms)])
    def test_piano_vocal_parts_and_ranges(self):
        t=get_template("piano_vocal")
        out=auto_arrange(self.sample(),t,"pop")
        self.assertEqual(len(out.parts),2)
        self.assertEqual(out.metadata["ensemble"],"Piano + Vocal")
        byid={i.id:i for i in t.instruments}
        for part in out.parts:
            spec=byid[part.id]
            for m in part.measures:
                for n in m.notes:
                    if n.pitch:
                        self.assertGreaterEqual(n.pitch.midi(),spec.low)
                        self.assertLessEqual(n.pitch.midi(),spec.high)
    def test_orchestra_has_all_template_parts(self):
        t=get_template("orchestra"); out=auto_arrange(self.sample(),t,"classical")
        self.assertEqual(len(out.parts),len(t.instruments))
