from __future__ import annotations

from dataclasses import dataclass
import sys

from .score import Measure, Note, Part, Pitch, Score


@dataclass(frozen=True)
class AudioBackendStatus:
    backend: str
    available: bool
    platform: str
    detail: str

    @property
    def summary(self) -> str:
        state = "ready" if self.available else "unavailable"
        return f"{self.backend}: {state} — {self.detail}"


def inspect_audio_output(output, platform: str | None = None) -> AudioBackendStatus:
    target_platform = sys.platform if platform is None else platform
    backend = type(output).__name__
    available = bool(getattr(output, "available", False))
    reason = str(getattr(output, "reason", "") or "").strip()

    if available:
        detail = "native speaker playback backend is available"
    elif reason:
        detail = reason
    else:
        detail = "no native speaker playback backend is available"

    return AudioBackendStatus(
        backend=backend,
        available=available,
        platform=target_platform,
        detail=detail,
    )


def build_speaker_test_score() -> Score:
    """Return a short A4 test tone score that exercises the normal audio renderer."""
    return Score(
        title="Speaker Test",
        parts=[
            Part(
                "TEST",
                "Speaker Test",
                measures=[
                    Measure(
                        1,
                        notes=[Note(Pitch("A", 4), duration=0.5, velocity=72)],
                        tempo=120.0,
                    )
                ],
            )
        ],
    )
