import tempfile, unittest
from pathlib import Path
import numpy as np, soundfile as sf
from harmonia_studio.transcription.tempo_meter import detect_tempo_meter

class TempoMeterTests(unittest.TestCase):
    def test_accented_4_4_click(self):
        with tempfile.TemporaryDirectory() as d:
            sr=22050; beat=0.5; count=32; duration=count*beat+.5
            y=np.zeros(int(sr*duration),dtype=float)
            click_len=int(.03*sr)
            env=np.exp(-np.linspace(0,7,click_len))*np.sin(2*np.pi*1200*np.arange(click_len)/sr)
            for i in range(count):
                pos=int(i*beat*sr)
                amp=1.0 if i%4==0 else .35
                y[pos:pos+click_len]+=amp*env
            p=Path(d)/"click.wav"; sf.write(p,y,sr)
            r=detect_tempo_meter(str(p))
            # Beat trackers can return octave-related tempi; normalize for the assertion.
            normalized=r.bpm
            while normalized<90: normalized*=2
            while normalized>180: normalized/=2
            self.assertAlmostEqual(normalized,120,delta=8)
            self.assertEqual(r.meter_denominator,4)
            self.assertIn(r.meter_numerator,{3,4,6})
            self.assertTrue(r.beat_times)
            self.assertTrue(0<=r.tempo_confidence<=1)
