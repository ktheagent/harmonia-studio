import time, unittest
from harmonia_studio.score import *
from harmonia_studio.playback import PlaybackEngine,PlaybackState

class PlaybackTests(unittest.TestCase):
    def sample(self):
        m=Measure(1,tempo=120,notes=[
            Note(Pitch("C",4),1,onset=0,velocity=100),
            Note(Pitch("E",4),1,onset=1,velocity=80)])
        return Score(parts=[Part("P1","P",measures=[m])])
    def test_schedule(self):
        e=PlaybackEngine(); ev=e.schedule(self.sample())
        self.assertEqual(len(ev),2)
        self.assertAlmostEqual(ev[1].time_seconds,0.5,places=4)
    def test_volume_mute_solo(self):
        s=self.sample(); e=PlaybackEngine()
        e.set_volume(0,.5); self.assertEqual(e.schedule(s)[0].velocity,50)
        e.mute(0); self.assertEqual(e.schedule(s),[])
        e.mute(0,False); e.solo(0); self.assertEqual(len(e.schedule(s)),2)
    def test_loop_and_seek(self):
        s=self.sample(); e=PlaybackEngine(); e.set_loop(0,0)
        self.assertEqual(len(e.schedule(s)),2); e.seek_measure(4); self.assertEqual(e.cursor_measure,4)
    def test_play_stop(self):
        got=[]; e=PlaybackEngine(got.append)
        e.tempo_factor=100
        e.play(self.sample()); time.sleep(.03)
        self.assertTrue(got)
        e.stop(); self.assertEqual(e.state,PlaybackState.STOPPED)
