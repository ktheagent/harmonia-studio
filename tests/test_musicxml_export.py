import tempfile, unittest
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.exporters.musicxml import export_musicxml
from harmonia_studio.importers.musicxml import import_musicxml

class MusicXMLExportTests(unittest.TestCase):
    def sample(self):
        m=Measure(
            1,
            time=TimeSignature(3,4),
            key=KeySignature(-1,"major"),
            tempo=96,
            notes=[Note(Pitch("F",4),1,voice=1,lyrics=[Lyric("La")]), Note(None,2,voice=1)],
            harmonies=[Harmony("F","major",symbol="F")],
        )
        return Score("Export Test","Composer",[Part("P1","Voice",measures=[m])])

    def test_roundtrip_musicxml(self):
        with tempfile.TemporaryDirectory() as d:
            p=export_musicxml(self.sample(),Path(d)/"x.musicxml")
            s=import_musicxml(p)
            self.assertEqual(s.title,"Export Test")
            self.assertEqual(s.parts[0].measures[0].time.beats,3)
            self.assertEqual(s.parts[0].measures[0].notes[0].pitch.midi(),65)
            self.assertEqual(s.parts[0].measures[0].notes[0].lyrics[0].text,"La")
            self.assertEqual(s.parts[0].measures[0].harmonies[0].root,"F")

    def test_roundtrip_mxl(self):
        with tempfile.TemporaryDirectory() as d:
            p=export_musicxml(self.sample(),Path(d)/"x.mxl")
            self.assertEqual(import_musicxml(p).parts[0].name,"Voice")
