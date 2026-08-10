import unittest
from harmonia_studio.score import *
from harmonia_studio.analysis.phrases import analyze_phrases, classify_cadence
from harmonia_studio.analysis.chords import detect_pitch_class_chord
from harmonia_studio.analysis.functions import analyze_function
from harmonia_studio.analysis.tonal import KeyEstimate

class PhraseTests(unittest.TestCase):
    def f(self,notes):
        return analyze_function(detect_pitch_class_chord(notes),KeyEstimate("C","major",1,1))
    def test_cadences(self):
        v=self.f([55,59,62,65]); i=self.f([60,64,67]); iv=self.f([53,57,60]); vi=self.f([57,60,64])
        self.assertEqual(classify_cadence(v,i,3).kind,"authentic")
        self.assertEqual(classify_cadence(iv,i,3).kind,"plagal")
        self.assertEqual(classify_cadence(v,vi,3).kind,"deceptive")
        self.assertEqual(classify_cadence(i,v,3).kind,"half")
    def test_phrase_boundaries_and_repetition(self):
        measures=[]
        for i in range(8):
            notes=[Note(Pitch.from_midi(x),1,onset=j) for j,x in enumerate([60,62,64])]
            measures.append(Measure(i+1,notes=notes))
        s=Score(parts=[Part("P1","P",measures=measures)])
        a=analyze_phrases(s,4)
        self.assertEqual(a.phrase_boundaries,[3,7])
        self.assertTrue(a.repeated_motifs)
        self.assertEqual(a.sections,[(0,3),(4,7)])
