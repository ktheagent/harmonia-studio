import tempfile,unittest
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.exporters.practice_tracks import export_practice_tracks

class PracticeTrackTests(unittest.TestCase):
    def sample(self):
        parts=[]
        for name,pitch in [("Soprano",72),("Alto",67),("Tenor",60),("Bass",48)]:
            parts.append(Part(name[0],name,Instrument("Voice",52),[Measure(1,tempo=120,notes=[Note(Pitch.from_midi(pitch),1,onset=0)])]))
        parts.append(Part("P","Piano",Instrument("Piano",0),[Measure(1,tempo=120,notes=[Note(Pitch("C",4),1,onset=0)])]))
        return Score(parts=parts)
    def test_practice_track_set(self):
        with tempfile.TemporaryDirectory() as d:
            files=export_practice_tracks(self.sample(),d,"wav",8000)
            for key in ["full_mix","soprano_emphasized","alto_emphasized","tenor_emphasized","bass_emphasized","instrument_only"]:
                self.assertIn(key,files)
                self.assertTrue(files[key].exists())
                self.assertGreater(files[key].stat().st_size,100)
