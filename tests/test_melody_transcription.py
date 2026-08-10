import tempfile, unittest
from pathlib import Path
import numpy as np, soundfile as sf
from harmonia_studio.transcription.melody import transcribe_melody

class MelodyTranscriptionTests(unittest.TestCase):
    def test_a4_tone_transcribes_near_midi69(self):
        with tempfile.TemporaryDirectory() as d:
            sr=22050; duration=1.2; t=np.arange(int(sr*duration))/sr
            env=np.minimum(1,t/.05)*np.minimum(1,(duration-t)/.05)
            y=.25*np.sin(2*np.pi*440*t)*np.clip(env,0,1)
            p=Path(d)/"a4.wav"; sf.write(p,y,sr)
            r=transcribe_melody(str(p),120)
            self.assertTrue(r.notes)
            med=round(np.median([n.midi for n in r.notes]))
            self.assertEqual(med,69)
            self.assertTrue(r.score.parts[0].measures)
            self.assertTrue(0<=r.confidence<=1)
