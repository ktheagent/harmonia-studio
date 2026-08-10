import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.satb import harmonize_satb
from harmonia_studio.quality import analyze_quality

class QualityTests(unittest.TestCase):
    def melody(self):
        ms=[Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)]) for i,p in enumerate([72,74,71,72])]
        return Score(parts=[Part("P1","Melody",measures=ms)])
    def test_quality_report(self):
        ref=self.melody(); out=harmonize_satb(ref); out.metadata["harmonyStyle"]="hymn"
        r=analyze_quality(out,ref,"hymn")
        self.assertEqual(r.metrics.melody_preservation,100)
        self.assertEqual(r.metrics.style_consistency,100)
        self.assertTrue(0<=r.metrics.overall<=100)
    def test_range_penalty(self):
        ref=self.melody(); out=harmonize_satb(ref)
        out.parts[0].measures[0].notes[0].pitch=Pitch.from_midi(100)
        r=analyze_quality(out,ref)
        self.assertLess(r.metrics.range_compliance,100)
        self.assertGreater(r.issue_counts.get("range",0),0)
