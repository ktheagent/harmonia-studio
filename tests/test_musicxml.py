import tempfile
import unittest
import zipfile
from pathlib import Path
from harmonia_studio.importers.musicxml import import_musicxml

XML = '''<?xml version="1.0"?>
<score-partwise version="4.0">
<work><work-title>Test Song</work-title></work>
<identification><creator type="composer">Tester</creator></identification>
<part-list><score-part id="P1"><part-name>Voice</part-name></score-part></part-list>
<part id="P1"><measure number="1">
<attributes><divisions>2</divisions><key><fifths>0</fifths><mode>major</mode></key><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
<harmony><root><root-step>C</root-step></root><kind text="C">major</kind></harmony>
<note><pitch><step>C</step><octave>4</octave></pitch><duration>2</duration><voice>1</voice><lyric><text>Hi</text></lyric></note>
<note><rest/><duration>2</duration><voice>1</voice></note>
</measure></part></score-partwise>'''

class MusicXMLTests(unittest.TestCase):
    def test_import_musicxml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.musicxml"
            p.write_text(XML)
            s = import_musicxml(p)
            self.assertEqual(s.title, "Test Song")
            self.assertEqual(s.composer, "Tester")
            self.assertEqual(s.parts[0].measures[0].notes[0].pitch.midi(), 60)
            self.assertTrue(s.parts[0].measures[0].notes[1].is_rest)
            self.assertEqual(s.parts[0].measures[0].harmonies[0].root, "C")

    def test_import_mxl(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.mxl"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("score.musicxml", XML)
            self.assertEqual(import_musicxml(p).parts[0].name, "Voice")
