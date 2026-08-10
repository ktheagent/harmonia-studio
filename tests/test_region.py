import unittest, json
from harmonia_studio.score import *
from harmonia_studio.harmony.region import reharmonize_region

class RegionTests(unittest.TestCase):
    def sample(self):
        ms=[]
        for i,p in enumerate([72,74,76,77,79,77]):
            ms.append(Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)],harmonies=[Harmony("C",symbol="OLD")]))
        return Score(parts=[Part("P1","Melody",measures=ms)])
    def test_only_selected_measures_change(self):
        s=self.sample()
        before=[json.dumps(m,default=lambda o:o.__dict__,sort_keys=True) for m in s.parts[0].measures]
        out=reharmonize_region(s,2,3,"jazz","balanced")
        after=[json.dumps(m,default=lambda o:o.__dict__,sort_keys=True) for m in out.parts[0].measures]
        for i in [0,1,4,5]: self.assertEqual(before[i],after[i])
        self.assertNotEqual(before[2],after[2])
        self.assertNotEqual(before[3],after[3])
