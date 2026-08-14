from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import wave

import numpy as np

from .exporters.audio import render_score_audio
from .score import Part, Score


def score_fragment(score: Score, start_measure: int = 0, end_measure: int | None = None) -> Score:
    """Return a score fragment containing the requested measure range."""
    start = max(0, int(start_measure))
    end = None if end_measure is None else max(start, int(end_measure))
    parts: list[Part] = []
    for part in score.parts:
        stop = None if end is None else end + 1
        parts.append(
            Part(
                id=part.id,
                name=part.name,
                instrument=part.instrument,
                measures=list(part.measures[start:stop]),
            )
        )
    return Score(
        title=score.title,
        composer=score.composer,
        parts=parts,
        metadata=dict(score.metadata),
    )


def write_pcm16_wave(path: str | Path, audio: np.ndarray, sample_rate: int) -> Path:
    """Write mono float audio to a standard PCM16 WAV without extra dependencies."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    samples = np.asarray(audio, dtype=np.float32)
    samples = np.clip(samples, -1.0, 1.0)
    pcm = np.rint(samples * 32767.0).astype("<i2")
    with wave.open(str(target), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wavsetframerate(int(sample_rate))
        wawwriteframes(pcm.tobytes())
    return target


class NullAudioOutput:
    """Fallback backend used where native Windows playback is unavailable."""

    available = False

    def __init__(self, reason: str = "Native Windows audio output is unavailable on this platform"):
        self.reason = reason

    def play(
        self,
        score: Score,
        *,
        start_measure: int = 0,
        loop_measure: int | None = None,
        part_volumes: dict[int, float] | None = None,
    ) -> None:
        return None

    def stop(self) -> None:
        return None

    def close(self) -> None:
        return None


class WindowsWaveOutput:
    """Render the score to a temporary WAV and play it through WinMM/winsound."""

    available = True

    def __init__(
        self,
        *,
        sample_rate: int = 44100,
        winsound_module=None,
        renderer=render_score_audio,
        writer=write_pcm16_wave,
    ):
        if winsound_module is None:
            import winsound as winsound_module
        self._winsound = winsound_module
        self._renderer = renderer
        self._writer = writer
        self.sample_rate = int(sample_rate)
        self._temp = TemporaryDirectory(prefix="harmonia-playback-")
        self._wave_path = Path(self._temp.name) / "playback.wav"
        self._closed = False

    def play(
        self,
        score: Score,
        *,
        start_measure: int = 0,
        loop_measure: int | None = None,
        part_volumes: dict[int, float] | None = None,
    ) -> None:
        if self._closed:
            raise RuntimeError("Audio output is closed")

        if loop_measure is not None:
            start = max(0, int(loop_measure))
            fragment = score_fragment(score, start, start)
        else:
            start = max(0, int(start_measure))
            fragment = score_fragment(score, start)

        audio = self._renderer(
            fragment,
            sample_rate=self.sample_rate,
            part_volumes=part_volumes,
        )
        self._writer(self._wave_path, audio, self.sample_rate)

        flags = self._winsound.SND_FILENAME | self._winsound.SND_ASYNC
        if loop_measure is not None:
            flags |= self._winsound.SND_LOOP
        self._winsound.PlaySound(str(self._wave_path), flags)

    def stop(self) -> None:
        if not self._closed:
            self._winsound.PlaySound(None, 0)

    def close(self) -> None:
        if self._closed:
            return
        self.stop()
        self._closed = True
        self._temp.cleanup()


def create_audio_output(platform: str | None = None):
    """Create the native playback backend for the current platform."""
    target = sys.platform if platform is None else platform
    if target != "win32":
        return NullAudioOutput()
    try:
        return WindowsWaveOutput()
    except Exception as exc:
        return NullAudioOutput(f"Windows audio backend unavailable: {exc}")
