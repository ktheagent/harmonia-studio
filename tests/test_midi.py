import tempfile, unittest
from pathlib import Path
from harmonia_studio.importers.midi import import_midi

class MidiTests(unittest.TestCase):
    def test_midi_import_and_quantize(self):
        import pretty_midi
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.mid"
            pm=pretty_midi.PrettyMIDI(initial_tempo=100)
            inst=pretty_midi.Instrument(program=0,name="Piano")
            inst.notes.append(pretty_midi.Note(velocity=90,pitch=60,start=0.01,end=0.49))
            inst.notes.append(pretty_midi.Note(velocity=80,pitch=64,start=0.51,end=1.0))
            pm.instruments.append(inst); pm.write(str(p))
            s=import_midi(p,0.25)
            self.assertEqual(s.parts[0].name,"Piano")
            self.assertEqual(s.parts[0].measures[0].notes[0].pitch.midi(),60)
            self.assertEqual(s.parts[0].instrument.midi_program,0)
            self.assertGreater(len(s.parts[0].measures[0].notes),1)
