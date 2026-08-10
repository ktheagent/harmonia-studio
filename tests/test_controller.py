from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from harmonia_studio.controller import StudioController
from harmonia_studio.score import (
    Score, Part, Instrument, Measure, Note, Pitch, Harmony, TimeSignature, KeySignature
)
from harmonia_studio.importers.musicxml import import_musicxml
from harmonia_studio.importers.midi import import_midi
from harmonia_studio.exporters.pdf_score import validate_pdf_file
from harmonia_studio.importers.audio import probe_audio


def demo_score() -> Score:
    notes = [
        Note(Pitch("C", 4), 1.0, onset=0.0),
        Note(Pitch("E", 4), 1.0, onset=1.0),
        Note(Pitch("G", 4), 1.0, onset=2.0),
        Note(Pitch("C", 5), 1.0, onset=3.0),
    ]
    m = Measure(
        1, notes=notes, harmonies=[Harmony("C", "major", symbol="C")],
        time=TimeSignature(4, 4), key=KeySignature(0, "major"), tempo=120.0,
    )
    return Score("Integration Demo", "Harmonia Studio", [Part("P1", "Melody", Instrument("Piano", 0), [m])])


class StudioControllerTests(unittest.TestCase):
    def test_analyze_harmonize_arrange_workflow(self):
        ctl = StudioController(demo_score())
        analysis = ctl.analyze()
        self.assertIn(analysis.tonality.global_key.tonic, {"C", "A"})
        arranged, candidates = ctl.harmonize("hymn")
        self.assertEqual(len(candidates), 3)
        self.assertEqual(len(arranged.parts), 4)
        final = ctl.arrange("piano_vocal", "pop")
        self.assertGreaterEqual(len(final.parts), 2)

    def test_export_and_reimport_interchange_formats(self):
        ctl = StudioController(demo_score())
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            xml = ctl.export_file(d / "roundtrip.musicxml")
            midi = ctl.export_file(d / "roundtrip.mid")
            pdf = ctl.export_file(d / "score.pdf")
            wav = ctl.export_file(d / "mix.wav")
            self.assertTrue(import_musicxml(xml).parts)
            self.assertTrue(import_midi(midi).parts)
            self.assertTrue(validate_pdf_file(pdf))
            info = probe_audio(wav)
            self.assertGreater(info.duration, 0)

    def test_import_export_musicxml_through_controller(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "source.musicxml"
            source_ctl = StudioController(demo_score())
            source_ctl.export_file(p)
            ctl = StudioController()
            outcome = ctl.import_file(p)
            self.assertEqual(outcome.source_kind, "musicxml")
            self.assertEqual(ctl.require_score().title, "Integration Demo")


if __name__ == "__main__":
    unittest.main()
