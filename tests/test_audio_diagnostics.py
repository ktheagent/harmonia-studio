import unittest

from harmonia_studio.audio_diagnostics import build_speaker_test_score, inspect_audio_output
from harmonia_studio.audio_output import NullAudioOutput


class ReadyOutput:
    available = True


class AudioDiagnosticsTests(unittest.TestCase):
    def test_available_backend_status(self):
        status = inspect_audio_output(ReadyOutput(), platform="win32")
        self.assertTrue(status.available)
        self.assertEqual(status.backend, "ReadyOutput")
        self.assertEqual(status.platform, "win32")
        self.assertIn("ready", status.summary)

    def test_null_backend_preserves_reason(self):
        output = NullAudioOutput("speaker device unavailable")
        status = inspect_audio_output(output, platform="linux")
        self.assertFalse(status.available)
        self.assertEqual(status.detail, "speaker device unavailable")
        self.assertIn("unavailable", status.summary)

    def test_speaker_test_score_is_short_a4(self):
        score = build_speaker_test_score()
        self.assertEqual(len(score.parts), 1)
        self.assertEqual(len(score.parts[0].measures), 1)
        note = score.parts[0].measures[0].notes[0]
        self.assertEqual(note.pitch.midi(), 69)
        self.assertEqual(note.duration, 0.5)
        self.assertEqual(note.velocity, 72)

    def test_speaker_test_score_uses_normal_score_model(self):
        score = build_speaker_test_score()
        self.assertEqual(score.title, "Speaker Test")
        self.assertEqual(score.parts[0].name, "Speaker Test")
        self.assertEqual(score.parts[0].measures[0].tempo, 120.0)


if __name__ == "__main__":
    unittest.main()
