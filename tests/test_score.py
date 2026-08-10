import unittest, json
from harmonia_studio.score import *

class ScoreModelTests(unittest.TestCase):
    def sample(self):
        m=Measure(1,time=TimeSignature(3,4),notes=[
            Note(Pitch("C",4),1,voice=1,lyrics=[Lyric("Hel")]),
            Note(Pitch("E",4),2,voice=2,lyrics=[Lyric("lo")]),
        ], harmonies=[Harmony("C","major",symbol="C")])
        return Score("Song","Composer",[Part("P1","Voice",measures=[m])])
    def test_pitch_midi_roundtrip(self):
        for n in [48,60,61,72]:
            self.assertEqual(Pitch.from_midi(n).midi(), n)
    def test_score_roundtrip(self):
        s=self.sample(); x=Score.from_dict(json.loads(json.dumps(s.to_dict())))
        self.assertEqual(x.parts[0].measures[0].notes[0].pitch.step,"C")
        self.assertEqual(x.parts[0].measures[0].time.beats,3)
        self.assertEqual(x.parts[0].measures[0].harmonies[0].symbol,"C")
        self.assertEqual(x.parts[0].measures[0].notes[0].lyrics[0].text,"Hel")
        self.assertEqual(x.parts[0].measures[0].notes[1].voice,2)
