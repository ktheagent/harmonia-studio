import unittest
from harmonia_studio.score import *
from harmonia_studio.assistant import parse_music_command,execute_music_command

class AssistantTests(unittest.TestCase):
    def sample(self):
        ms=[Measure(i+1,notes=[Note(Pitch.from_midi(72+(i%3)),4,onset=0)]) for i in range(20)]
        return Score(parts=[Part("P1","Melody",measures=ms)])
    def test_parse_region_gospel_and_constraints(self):
        c=parse_music_command("Reharmonize measures 9-16 in modern gospel style, keep the soprano unchanged and make the tenor easier.")
        self.assertEqual(c.style,"gospel")
        self.assertEqual(c.measure_range,(8,15))
        self.assertIn("tenor",c.easier_voices)
        self.assertEqual(c.action,"reharmonize-region")
    def test_parse_candidates(self):
        c=parse_music_command("Create three alternatives in jazz style")
        self.assertEqual(c.candidate_count,3); self.assertEqual(c.style,"jazz")
    def test_execute_routes_through_quality(self):
        r=execute_music_command(self.sample(),"Turn this melody into SATB in hymn style and make the tenor easier")
        self.assertEqual(len(r.score.parts),4)
        self.assertTrue(0<=r.quality.metrics.overall<=100)
        self.assertIn("assistantCommand",r.score.metadata)
    def test_three_candidates_execute(self):
        r=execute_music_command(self.sample(),"Create 3 alternatives in pop style")
        self.assertEqual(len(r.candidates),3)
