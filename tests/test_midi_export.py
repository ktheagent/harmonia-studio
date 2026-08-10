import tempfile,unittest
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.exporters.midi import export_midi
from harmonia_studio.importers.midi import import_midi

class MidiExportTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            m=Measure(1,tempo=100,notes=[Note(Pitch("C",4),1,onset=0,velocity=90),Note(Pitch("E",4),1,onset=1)])
            s=Score("MIDI","",[Part("P1","Piano",Instrument("Piano",0),[m])])
            p=export_midi(s,Path(d)/"x.mid")
            out=import_midi(p,.25)
            pitches=[n.pitch.midi() for n in out.parts[0].measures[0].notes]
            self.assertEqual(pitches,[60,64])
            self.assertEqual(out.parts[0].name,"Piano")
