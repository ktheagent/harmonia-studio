import tempfile, unittest
from pathlib import Path
import numpy as np, soundfile as sf
from harmonia_studio.importers.audio import probe_audio,load_audio

class AudioImportTests(unittest.TestCase):
    def test_wav_import(self):
        with tempfile.TemporaryDirectory() as d:
            sr=22050; t=np.arange(sr)/sr; y=.2*np.sin(2*np.pi*440*t)
            p=Path(d)/"tone.wav"; sf.write(p,y,sr)
            info=probe_audio(p)
            self.assertEqual(info.sample_rate,sr)
            self.assertAlmostEqual(info.duration,1,places=1)
            data=load_audio(p,sr)
            self.assertEqual(data.sample_rate,sr)
            self.assertGreater(len(data.samples),20000)
    def test_flac_import(self):
        with tempfile.TemporaryDirectory() as d:
            sr=8000; p=Path(d)/"x.flac"; sf.write(p,np.zeros(sr),sr)
            self.assertEqual(probe_audio(p).format,"flac")
