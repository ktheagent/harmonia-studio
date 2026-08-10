import tempfile,unittest,shutil
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.exporters.audio import export_audio,render_score_audio
from harmonia_studio.importers.audio import probe_audio

class AudioExportTests(unittest.TestCase):
    def sample(self):
        m=Measure(1,tempo=120,notes=[Note(Pitch("A",4),1,onset=0,velocity=100),Note(Pitch("C",5),1,onset=1)])
        return Score(parts=[Part("P1","Tone",measures=[m])])
    def test_wav_export(self):
        with tempfile.TemporaryDirectory() as d:
            p=export_audio(self.sample(),Path(d)/"x.wav",22050)
            info=probe_audio(p)
            self.assertEqual(info.sample_rate,22050)
            self.assertGreater(info.duration,.9)
            self.assertGreater(abs(render_score_audio(self.sample(),8000)).max(),0)
    @unittest.skipUnless(shutil.which("ffmpeg"),"ffmpeg not installed")
    def test_mp3_export(self):
        with tempfile.TemporaryDirectory() as d:
            p=export_audio(self.sample(),Path(d)/"x.mp3",22050)
            self.assertTrue(p.exists()); self.assertGreater(p.stat().st_size,1000)
            self.assertGreater(probe_audio(p).duration,.9)
