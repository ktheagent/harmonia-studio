import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.voice_leading import validate_voice_leading,VoiceLeadingProfile

class VoiceLeadingTests(unittest.TestCase):
    def make(self,lines):
        parts=[]
        for i,line in enumerate(lines):
            notes=[Note(Pitch.from_midi(p),1,onset=j) for j,p in enumerate(line)]
            parts.append(Part(f"P{i}",f"V{i}",measures=[Measure(1,notes=notes)]))
        return Score(parts=parts)
    def test_parallel_fifth_detected(self):
        # S and A move C-G to D-A: parallel fifth
        s=self.make([[72,74],[65,67],[60,60],[48,48]])
        codes={x.code for x in validate_voice_leading(s)}
        self.assertIn("parallel-fifth",codes)
    def test_range_and_crossing(self):
        s=self.make([[50],[60],[55],[48]])
        codes={x.code for x in validate_voice_leading(s)}
        self.assertIn("range",codes)
        self.assertIn("voice-crossing",codes)
    def test_excessive_leap(self):
        s=self.make([[60,79],[55,55],[50,50],[43,43]])
        self.assertIn("excessive-leap",{x.code for x in validate_voice_leading(s)})
