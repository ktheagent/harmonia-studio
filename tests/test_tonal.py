import unittest
from harmonia_studio.score import *
from harmonia_studio.analysis.tonal import analyze_tonality,scale_pitch_classes

class TonalTests(unittest.TestCase):
    def score(self,pitches):
        notes=[Note(Pitch.from_midi(p),1,onset=i) for i,p in enumerate(pitches)]
        return Score(parts=[Part("P1","P",measures=[Measure(1,notes=notes)])])
    def test_c_major_detection(self):
        # tonic/dominant weighted heavily
        a=analyze_tonality(self.score([60,64,67,60,67,65,62,59,60,64,67]))
        self.assertEqual(a.global_key.tonic,"C")
        self.assertEqual(a.global_key.mode,"major")
        self.assertIn(0,scale_pitch_classes(a.global_key))
    def test_has_local_keys(self):
        a=analyze_tonality(self.score([60,64,67]))
        self.assertEqual(len(a.local_keys),1)
        self.assertGreaterEqual(a.global_key.confidence,0)
