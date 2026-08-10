import unittest
from harmonia_studio.score import *
from harmonia_studio.analysis.chords import detect_pitch_class_chord,analyze_chords,apply_chord_analysis

class ChordTests(unittest.TestCase):
    def test_c_major(self):
        c=detect_pitch_class_chord([60,64,67])
        self.assertEqual(c.root_name,"C")
        self.assertEqual(c.quality,"major")
        self.assertEqual(c.symbol,"C")
    def test_g7(self):
        c=detect_pitch_class_chord([55,59,62,65])
        self.assertEqual(c.root_name,"G")
        self.assertEqual(c.quality,"dominant-seventh")
        self.assertIn("7",c.symbol)
    def test_analysis_harmonic_rhythm_and_apply(self):
        m=Measure(1,notes=[
            Note(Pitch("C",4),1,onset=0),Note(Pitch("E",4),1,onset=0),Note(Pitch("G",4),1,onset=0),
            Note(Pitch("G",3),1,onset=2),Note(Pitch("B",3),1,onset=2),Note(Pitch("D",4),1,onset=2)])
        s=Score(parts=[Part("P1","P",measures=[m])])
        cs=analyze_chords(s)
        self.assertEqual(len(cs),2)
        self.assertEqual(cs[0].duration,2)
        apply_chord_analysis(s); self.assertEqual(len(s.parts[0].measures[0].harmonies),2)
