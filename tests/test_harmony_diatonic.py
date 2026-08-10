import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.diatonic import harmonize_diatonic,apply_harmony_plan

class DiatonicHarmonyTests(unittest.TestCase):
    def sample(self):
        ms=[]
        for i,pitches in enumerate([[60,64,67],[65,69,72],[67,71,74],[60,64,67]]):
            ms.append(Measure(i+1,notes=[Note(Pitch.from_midi(p),1,onset=j) for j,p in enumerate(pitches)]))
        return Score("Tune","",[Part("P1","Melody",measures=ms)])
    def test_harmonize_preserves_melody(self):
        s=self.sample(); before=[n.pitch.midi() for n in s.iter_notes()]
        p=harmonize_diatonic(s)
        out=apply_harmony_plan(s,p)
        self.assertEqual(before,[n.pitch.midi() for n in out.iter_notes()])
        self.assertEqual(len(p.choices),4)
        self.assertTrue(all(c.quality in {"major","minor","diminished"} for c in p.choices))
        self.assertTrue(out.parts[0].measures[-1].harmonies)
    def test_beat_density(self):
        p=harmonize_diatonic(self.sample(),"beat")
        self.assertGreater(len(p.choices),4)
