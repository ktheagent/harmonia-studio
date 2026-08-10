from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .score import Score
from .analysis.tonal import analyze_tonality
from .analysis.chords import analyze_chords
from .analysis.phrases import analyze_phrases
from .arrangement.engine import auto_arrange
from .harmony.candidates import generate_candidates, HarmonyCandidate
from .quality import analyze_quality, QualityReport
from .importers.musicxml import import_musicxml
from .importers.midi import import_midi
from .importers.omr import recognize_score, OMRResult
from .importers.audio import load_audio
from .transcription.melody import transcribe_melody
from .transcription.tempo_meter import detect_tempo_meter
from .exporters.musicxml import export_musicxml
from .exporters.midi import export_midi
from .exporters.pdf_score import export_pdf_score
from .exporters.audio import export_audio


@dataclass
class ImportOutcome:
    score: Score
    source_kind: str
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisBundle:
    tonality: Any
    chords: list[Any]
    phrases: Any
    quality: QualityReport


class StudioController:
    """Headless application workflow used by both the desktop UI and tests.

    The controller owns the current score and is the integration boundary between
    file adapters, analysis, harmonization, arrangement and export.
    """

    def __init__(self, score: Score | None = None):
        self.score = score
        self.last_import: ImportOutcome | None = None
        self.last_omr: OMRResult | None = None

    def require_score(self) -> Score:
        if self.score is None:
            raise ValueError("No score is loaded.")
        return self.score

    def set_score(self, score: Score) -> Score:
        self.score = score
        return score

    def import_file(self, path: str | Path) -> ImportOutcome:
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix in {".musicxml", ".xml", ".mxl"}:
            score = import_musicxml(p)
            outcome = ImportOutcome(score, "musicxml")
        elif suffix in {".mid", ".midi"}:
            score = import_midi(p)
            outcome = ImportOutcome(score, "midi")
        elif suffix in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            omr = recognize_score(p)
            self.last_omr = omr
            score = omr.score
            outcome = ImportOutcome(
                score,
                "omr",
                float(omr.confidence),
                list(omr.warnings),
                {"symbol_count": len(omr.symbols), "pages": len(omr.page_images)},
            )
        elif suffix in {".wav", ".mp3", ".flac", ".aac", ".m4a"}:
            audio = load_audio(p)
            timing = detect_tempo_meter(audio)
            melody = transcribe_melody(audio, bpm=timing.bpm)
            score = melody.score
            for part in score.parts:
                for measure in part.measures:
                    measure.tempo = timing.bpm
                    measure.time.beats = timing.meter_numerator
                    measure.time.beat_type = timing.meter_denominator
            score.metadata.update({
                "sourceFormat": suffix.lstrip(".").upper(),
                "sourcePath": str(p),
                "transcriptionConfidence": melody.confidence,
                "detectedBpm": timing.bpm,
                "detectedMeter": f"{timing.meter_numerator}/{timing.meter_denominator}",
            })
            outcome = ImportOutcome(
                score,
                "audio-transcription",
                float(melody.confidence),
                [],
                {
                    "bpm": timing.bpm,
                    "meter": f"{timing.meter_numerator}/{timing.meter_denominator}",
                    "notes": len(melody.notes),
                },
            )
        else:
            raise ValueError(f"Unsupported import format: {suffix or '(no extension)'}")

        self.score = score
        self.last_import = outcome
        return outcome

    def analyze(self) -> AnalysisBundle:
        score = self.require_score()
        return AnalysisBundle(
            analyze_tonality(score),
            analyze_chords(score),
            analyze_phrases(score),
            analyze_quality(score),
        )

    def harmonize(self, style: str = "hymn", candidate_index: int = 0) -> tuple[Score, list[HarmonyCandidate]]:
        source = self.require_score()
        candidates = generate_candidates(source, style)
        if not 0 <= candidate_index < len(candidates):
            raise IndexError("candidate_index is out of range")
        selected = candidates[candidate_index].result.score
        self.score = selected
        return selected, candidates

    def arrange(self, ensemble: str = "piano_vocal", style: str = "pop", complexity: str = "balanced") -> Score:
        score = auto_arrange(self.require_score(), ensemble, style, complexity)
        self.score = score
        return score

    def export_file(self, path: str | Path, pdf_mode: str = "full_score") -> Path:
        score = self.require_score()
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix in {".musicxml", ".xml", ".mxl"}:
            return export_musicxml(score, p)
        if suffix in {".mid", ".midi"}:
            return export_midi(score, p)
        if suffix == ".pdf":
            return export_pdf_score(score, p, mode=pdf_mode)
        if suffix in {".wav", ".mp3"}:
            return export_audio(score, p)
        raise ValueError("Supported exports: MusicXML/MXL, MIDI, PDF, WAV and MP3.")
