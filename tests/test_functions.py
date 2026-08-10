import unittest
from harmonia_studio.analysis.chords import detect_pitch_class_chord
from harmonia_studio.analysis.functions import analyze_function
from harmonia_studio.analysis.tonal import KeyEstimate

class FunctionTests(unittest.TestCase):
    def key(self): return KeyEstimate("C","major",1,1)
    def test_tonic_and_dominant(self):
        c=detect_pitch_class_chord([60,64,67])
        g=detect_pitch_class_chord([55,59,62,65])
        self.assertEqual(analyze_function(c,self.key()).roman,"I")
        fg=analyze_function(g,self.key())
        self.assertEqual(fg.roman,"V")
        self.assertEqual(fg.function,"dominant")
    def test_secondary_dominant(self):
        # A7 -> V/ii in C major
        a=detect_pitch_class_chord([57,61,64,67])
        f=analyze_function(a,self.key())
        self.assertEqual(f.roman,"V/ii")
        self.assertTrue(f.tonicization)
