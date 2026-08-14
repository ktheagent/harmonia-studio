import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from harmonia_studio.audio_output import (
    NullAudioOutput,
    WindowsWaveOutput,
    create_audio_output,
    score_fragment,
    write_pcm16_wav,
)
from harmonia_studio.score import Measure, Note, Part, Pitch, Score


class FakeWinSound:
    SND_FILENAME = 1
    SND_ASYNC = 2
    SND_LOOP = 4

    def __init__(self):
        self.calls = []

    def PlaySound(self, path, flags):
        self.calls.append((path, flags))


class AudioOutputTests(unittest.TestCase):
    def make_score(self):
        return Score(
            "Audio",
            parts=[
                Part(
                    "P1",
                    "Piano",
                    measures=[
                        Measure(1, notes=[Note(Pitch("C", 4), 1)]),
                        Measure(2, notes=[Note(Pitch("D", 4), 1)]),
                    ],
                )
            ],
        )

    def test_score_fragment_selects_requested_measure_range(self):
        fragment = score_fragment(self.make_score(), 1, 1)
        self.assertEqual(len(fragment.parts), 1)
        self.assertEqual(len(fragment.parts[0].measures), 1)
        self.assertEqual(fragment.parts[0].measures[0].number, 2)

    def test_pcm_writer_creates_standard_mono_16_bit_wav(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.wav"
            write_pcm16_wav(path, np.array([0.0, 0.5, -0.5], dtype=np.float32), 8000)
            with wave.open(str(path), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 8000)
                self.assertEqual(wav.getnframes(), 3)

    def test_non_windows_factory_returns_safe_fallback(self):
        backend = create_audio_output(platform="linux")
        self.assertIsInstance(backend, NullAudioOutput)
        self.assertFalse(backend.available)

    def test_windows_backend_uses_async_filename_flags(self):
        fake = FakeWinSound()
        def renderer(score, sample_rate=44100, part_volumes=None):
            return np.zeros(32, dtype=np.float32)
        def writer(path, audio, sample_rate):
            Path(path).write_bytes(b"RIFF")
            return Path(path)

        backend = WindowsWaveOutput(
            winsound_module=fake,
            renderer=renderer,
            writer=writer,
            sample_rate=8000,
        )
        try:
            backend.play(self.make_score())
            self.assertEqual(len(fake.calls), 1)
            path, flags = fake.calls[0]
            self.assertTrue(path.endswith("playback.wav"))
            self.assertEqual(flags, fake.SND_FILENAME | fake.SND_ASYNC)
            backend.stop()
            self.assertEqual(fake.calls[-1], (None, 0))
        finally:
            backend.close()

    def test_loop_playback_adds_loop_flag(self):
        fake = FakeWinSound()
        backend = WindowsWaveOutput(
            winsound_module=fake,
            renderer=lambda score, sample_rate=44100, part_volumes=None: np.zeros(8, dtype=np.float32),
            writer=lambda path, audio, sample_rate: Path(path),
         )
        try:
            backend.play(self.make_score(), loop_measure=0)
            self.assertEqual(
                fake.calls[0][1],
                fake.SND_FILENAME | fake.SND_ASYNC | fake.SND_LOOP,
            )
        finally:
            backend.close()


if __name__ == "__main__":
    unittest.main()
