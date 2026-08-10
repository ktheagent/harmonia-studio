import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.satb import harmonize_satb
from harmonia_studio.harmony.voice_leading import validate_voice_leading

class SATBTests(unittest.TestCase):
    def sample(self):
        ms=[]
        for i,p in enumerate([72,74,71,72]):
            ms.append(Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)]))
        return Score("Tune","",[Part("P1","Melody",measures=ms)])
    def test_four_parts_and_melody_preserved(self):
        s=self.sample(); out=harmonize_satb(s)
        self.assertEqual([p.name for p in out.parts],["Soprano","Alto","Tenor","Bass"])
        before=[n.pitch.midi() for n in s.parts[0].measures for n in n.notes]
        after=[n.pitch.midi() for m in out.parts[0].measures for n in m.notes]
        self.assertEqual(before,after)
    def test_generated_ranges_and_order(self):
        out=harmonize_satb(self.sample())
        issues=validate_voice_leading(out)
        self.assertFalse(any(i.code in {"range","voice-crossing"} for i in issues))
