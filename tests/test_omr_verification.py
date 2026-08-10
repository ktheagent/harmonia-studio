import unittest
from harmonia_studio.score import *
from harmonia_studio.importers.omr import OMRResult,OMRSymbol
from harmonia_studio.omr_verification import OMRVerificationSession

class OMRVerificationTests(unittest.TestCase):
    def result(self):
        s=Score(parts=[Part("P1","Recognized",measures=[Measure(1,notes=[Note(Pitch("C",4),1)])])])
        sy=[OMRSymbol(1,"notehead",(0,0,5,5),.4,Pitch("C",4))]
        return OMRResult(s,sy,.4,["low"],["page.png"])
    def test_uncertain_and_correction(self):
        v=OMRVerificationSession(self.result(),.7)
        self.assertEqual(len(v.uncertain_symbols()),1)
        v.correct_pitch(0,0,Pitch("D",4))
        self.assertEqual(v.score.parts[0].measures[0].notes[0].pitch.step,"D")
        out=v.approve(); self.assertTrue(out.metadata["omrVerified"])
        self.assertEqual(out.metadata["omrEditCount"],1)
    def test_add_delete(self):
        v=OMRVerificationSession(self.result())
        v.add_note(0,Note(Pitch("E",4),1)); self.assertEqual(len(v.score.parts[0].measures[0].notes),2)
        v.delete_note(0,1); self.assertEqual(len(v.score.parts[0].measures[0].notes),1)
