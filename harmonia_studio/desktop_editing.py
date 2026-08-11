from __future__ import annotations

from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class HarmonyEdit:
    root: str
    kind: str
    bass: str = ""
    symbol: str = ""

    def to_harmony(self):
        from .score import Harmony
        return Harmony(root=self.root, kind=self.kind, bass=self.bass, symbol=self.symbol)


_ROOT_RE = re.compile(
    r"^\s*([A-Ga-g])([#b]?)([^/]*?)(?:/([A-Ga-g])([#b]?))?\s*$"
)


def validate_duration(value: float) -> float:
    duration = float(value)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Duration must be a positive finite number")
    if duration > 64:
        raise ValueError("Duration is too large")
    return duration


def parse_harmony_symbol(text: str) -> HarmonyEdit | None:
    symbol = (text or "").strip()
    if not symbol:
        return None

    normalized = symbol.replace("♯", "#").replace("♭", "b")
    match = _ROOT_RE.match(normalized)
    if not match:
        raise ValueError("Harmony must start with A-G, optionally #/b, for example Cmaj7 or F#m7/C#")

    root = match.group(1).upper() + (match.group(2) or "")
    suffix = (match.group(3) or "").strip()
    bass_step = match.group(4)
    bass = ""
    if bass_step:
        bass = bass_step.upper() + (match.group(5) or "")

    kind = _kind_from_suffix(suffix)
    return HarmonyEdit(root=root, kind=kind, bass=bass, symbol=symbol)


def _kind_from_suffix(suffix: str) -> str:
    raw = suffix.strip()
    low = raw.lower().replace("Δ", "maj").replace("°", "dim")

    if low in {"", "maj", "major"}:
        return "major"
    if low in {"m", "min", "minor"}:
        return "minor"
    if low.startswith(("maj7", "major7")):
        return "major-seventh"
    if low.startswith(("m7", "min7", "minor7")):
        return "minor-seventh"
    if low.startswith(("dim", "o")):
        return "diminished"
    if low.startswith(("aug", "+")):
        return "augmented"
    if low.startswith("sus"):
        return "suspended"
    if low.startswith("7"):
        return "dominant"
    return "other"
