import unittest
from harmonia_studio.score import *
from harmonia_studio.editor import ScoreEditor

def sample():
    return Score(parts=[Part("P1","P",measures=[Measure(1,notes=[Note(Pitch("C",4),1)])])])

class EditorTests(unittest.TestCase):
    def test_add_remove_undo_redo(self):
        s=sample(); e=ScoreEditor(s)
        e.add_note(0,0,Note(Pitch("E",4),1))
        self.assertEqual(len(s.parts[0].measures[0].notes),2)
        self.assertTrue(e.undo()); self.assertEqual(len(s.parts[0].measures[0].notes),1)
        self.assertTrue(e.redo()); self.assertEqual(len(s.parts[0].measures[0].notes),2)
        e.remove_note(0,0,1); self.assertEqual(len(s.parts[0].measures[0].notes),1)
    def test_transpose_undo(self):
        s=sample(); e=ScoreEditor(s); e.transpose(2)
        self.assertEqual(s.parts[0].measures[0].notes[0].pitch.midi(),62)
        e.undo(); self.assertEqual(s.parts[0].measures[0].notes[0].pitch.midi(),60)
    def test_duration_lyrics_harmony_measure(self):
        s=sample(); e=ScoreEditor(s)
        e.change_duration(0,0,0,2); self.assertEqual(s.parts[0].measures[0].notes[0].duration,2)
        e.set_lyrics(0,0,0,"Hello"); self.assertEqual(s.parts[0].measures[0].notes[0].lyrics[0].text,"Hello")
        e.set_harmony(0,0,0,Harmony("C",symbol="C")); self.assertEqual(s.parts[0].measures[0].harmonies[0].symbol,"C")
        e.add_measure(0); self.assertEqual(len(s.parts[0].measures),2)
