import tempfile,unittest
from pathlib import Path
import numpy as np,soundfile as sf
from harmonia_studio.transcription.chords import recognize_audio_chords

class AudioChordTests(unittest.TestCase):
    def test_c_major_triad(self):
        with tempfile.TemporaryDirectory() as d:
            sr=22050; t=np.arange(sr*2)/sr
            freqs=[261.6256,329.6276,391.9954]
            y=sum(np.sin(2*np.pi*f*t) for f in freqs)/len(freqs)*.25
            p=Path(d)/"c.wav"; sf.write(p,y,sr)
            r=recognize_audio_chords(str(p),1.0)
            self.assertTrue(r.segments)
            self.assertEqual(r.segments[0].root_name,"C")
            self.assertEqual(r.segments[0].quality,"major")
            r.correct(0,"F","minor")
            self.assertEqual(r.segments[0].symbol,"Fm")
            self.assertEqual(r.segments[0].confidence,1.0)
