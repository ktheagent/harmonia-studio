import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from harmonia_studio.score import Score, Part, Measure, Note, Pitch
from harmonia_studio.exporters.musicxml import export_musicxml
from harmonia_studio.importers.musicxml import import_musicxml

class PolyphonicMusicXMLTests(unittest.TestCase):
    def test_roundtrip_polyphonic_voices_preserve_onsets(self):
        score = Score("Poly", parts=[Part("P1", "Piano", measures=[Measure(
            1,
            notes=[
                Note(Pitch("C", 4), 2, voice=1, onset=0),
                Note(Pitch("D", 4), 2, voice=1, onset=2),
                Note(Pitch("G", 3), 4, voice=2, onset=0),
            ],
        )])])
        with tempfile.TemporaryDirectory() as d:
            path = export_musicxml(score, Path(d)/"poly.musicxml")
            root = ET.parse(path).getroot()
            self.assertIsNotNone(root.find(".//backup"))
            out = import_musicxml(path)
            notes = out.parts[0].measures[0].notes
            v1 = [n.onset for n in notes if n.voice == 1]
            v2 = [n.onset for n in notes if n.voice == 2]
            self.assertEqual(v1, [0.0, 2.0])
            self.assertEqual(v2, [0.0])

    def test_roundtrip_gap_uses_forward(self):
        score = Score("Gap", parts=[Part("P1", "Voice", measures=[Measure(
            1,
            notes=[
                Note(Pitch("C", 4), 1, voice=1, onset=0),
                Note(Pitch("D", 4), 1, voice=1, onset=2),
            ],
        )])])
        with tempfile.TemporaryDirectory() as d:
            path = export_musicxml(score, Path(d)/"gap.musicxml")
            root = ET.parse(path).getroot()
            forward = root.find(".//forward/duration")
            self.assertIsNotNone(forward)
            self.assertEqual(int(forward.text), 480)
            notes = import_musicxml(path).parts[0].measures[0].notes
            self.assertEqual([n.onset for n in notes], [0.0, 2.0])

    def test_roundtrip_chord_preserves_shared_onset(self):
        score = Score("Chord", parts=[Part("P1", "Voice", measures=[Measure(
            1,
            notes=[
                Note(Pitch("C", 4), 1, voice=1, onset=0),
                Note(Pitch("E", 4), 1, voice=1, onset=0),
                Note(Pitch("G", 4), 1, voice=1, onset=1),
            ],
        )])])
        with tempfile.TemporaryDirectory() as d:
            path = export_musicxml(score, Path(d)/"chord.musicxml")
            root = ET.parse(path).getroot()
            self.assertEqual(len(root.findall(".//chord")), 1)
            notes = import_musicxml(path).parts[0].measures[0].notes
            self.assertEqual([n.onset for n in notes], [0.0, 0.0, 1.0])

    def test_import_canonical_backup_forward_timeline(self):
        xml = """<score-partwise version='4.0'>
        <part-list><score-part id='P1'><part-name>Piano</part-name></score-part></part-list>
        <part id='P1'><measure number='1'>
          <attributes><divisions>2</divisions><time><beats>4</beats><beat-type>4</beat-type></time></attributes>
          <note><pitch><step>C</step><octave>4</octave></pitch><duration>4</duration><voice>1</voice></note>
          <forward><duration>2</duration></forward>
          <note><pitch><step>D</step><octave>4</octave></pitch><duration>2</duration><voice>1</voice></note>
          <backup><duration>8</duration></backup>
          <note><pitch><step>G</step><octave>3</octave></pitch><duration>8</duration><voice>2</voice></note>
        </measure></part></score-partwise>"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"canonical.musicxml"
            p.write_text(xml)
            notes = import_musicxml(p).parts[0].measures[0].notes
            self.assertEqual([(n.voice, n.onset) for n in notes], [(1, 0.0), (1, 3.0), (2, 0.0)])

if __name__ == "__main__":
    unittest.main()
