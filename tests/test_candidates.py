import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.candidates import generate_candidates

class CandidateTests(unittest.TestCase):
    def sample(self):
        ms=[Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)]) for i,p in enumerate([72,74,71,72])]
        return Score(parts=[Part("P1","Melody",measures=ms)])
    def test_three_distinct_candidates(self):
        cs=generate_candidates(self.sample(),"hymn")
        self.assertEqual([c.label for c in cs],["Conservative","Stylistic","Creative"])
        sigs={tuple((x.root_pc,x.quality,x.inversion) for x in c.result.plan.choices) for c in cs}
        self.assertEqual(len(sigs),3)
        self.assertTrue(all(0<=c.quality_score<=100 for c in cs))
