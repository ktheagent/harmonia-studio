import unittest,json,tempfile
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.history import ProjectHistory
from harmonia_studio.project import ProjectService

class HistoryTests(unittest.TestCase):
    def score(self,pitch):
        return Score(parts=[Part("P1","P",measures=[Measure(1,notes=[Note(Pitch.from_midi(pitch),1)])])])
    def test_undo_redo_named_restore(self):
        h=ProjectHistory(); a=h.named_version(self.score(60),"Original"); b=h.record_harmony_generation(self.score(62),"jazz")
        self.assertEqual(h.current().parts[0].measures[0].notes[0].pitch.midi(),62)
        self.assertEqual(h.undo().parts[0].measures[0].notes[0].pitch.midi(),60)
        self.assertEqual(h.redo().parts[0].measures[0].notes[0].pitch.midi(),62)
        self.assertEqual(h.restore("Original").parts[0].measures[0].notes[0].pitch.midi(),60)
    def test_serialization_and_project_persistence(self):
        h=ProjectHistory(); h.record_import(self.score(64),"source.musicxml")
        h2=ProjectHistory.from_dict(json.loads(json.dumps(h.to_dict())))
        self.assertEqual(h2.snapshots[0].kind,"import-source")
        with tempfile.TemporaryDirectory() as d:
            svc=ProjectService(Path(d)/"recent.json",Path(d)/"recovery")
            p=svc.new("History"); p.history=h.to_dict()
            path=svc.save(p,Path(d)/"x.harmonia")
            loaded=svc.open(path)
            self.assertEqual(loaded.history["snapshots"][0]["kind"],"import-source")
