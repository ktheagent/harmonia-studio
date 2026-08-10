from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from .score import Score, Note, Pitch, Measure, Harmony, Lyric

class ScoreEditor:
    """Non-destructive editor with snapshot-based undo/redo for MVP correctness."""
    def __init__(self, score: Score, history_limit: int = 100):
        self.score = score
        self.history_limit = history_limit
        self._undo: list[dict] = []
        self._redo: list[dict] = []

    def _snapshot(self) -> dict:
        return deepcopy(self.score.to_dict())

    def _restore(self, data: dict) -> None:
        restored = Score.from_dict(deepcopy(data))
        self.score.title = restored.title
        self.score.composer = restored.composer
        self.score.parts = restored.parts
        self.score.metadata = restored.metadata

    def _begin(self) -> None:
        self._undo.append(self._snapshot())
        if len(self._undo) > self.history_limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self) -> bool:
        if not self._undo:
            return False
        self._redo.append(self._snapshot())
        self._restore(self._undo.pop())
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        self._undo.append(self._snapshot())
        self._restore(self._redo.pop())
        return True

    def add_note(self, part_index: int, measure_index: int, note: Note) -> None:
        self._begin()
        self.score.parts[part_index].measures[measure_index].notes.append(deepcopy(note))

    def remove_note(self, part_index: int, measure_index: int, note_index: int) -> Note:
        self._begin()
        return self.score.parts[part_index].measures[measure_index].notes.pop(note_index)

    def change_duration(self, part_index: int, measure_index: int, note_index: int, duration: float) -> None:
        if duration <= 0:
            raise ValueError("Duration must be positive")
        self._begin()
        self.score.parts[part_index].measures[measure_index].notes[note_index].duration = duration

    def move_pitch(self, part_index: int, measure_index: int, note_index: int, semitones: int) -> None:
        note = self.score.parts[part_index].measures[measure_index].notes[note_index]
        if note.pitch is None:
            return
        self._begin()
        note.pitch = Pitch.from_midi(max(0, min(127, note.pitch.midi() + semitones)))

    def transpose(self, semitones: int, part_index: int | None = None) -> None:
        self._begin()
        parts = self.score.parts if part_index is None else [self.score.parts[part_index]]
        for part in parts:
            for measure in part.measures:
                for note in measure.notes:
                    if note.pitch is not None:
                        note.pitch = Pitch.from_midi(max(0, min(127, note.pitch.midi() + semitones)))

    def set_lyrics(self, part_index: int, measure_index: int, note_index: int, text: str) -> None:
        self._begin()
        self.score.parts[part_index].measures[measure_index].notes[note_index].lyrics = [Lyric(text)] if text else []

    def set_harmony(self, part_index: int, measure_index: int, harmony_index: int, harmony: Harmony) -> None:
        self._begin()
        hs = self.score.parts[part_index].measures[measure_index].harmonies
        if harmony_index < len(hs):
            hs[harmony_index] = deepcopy(harmony)
        else:
            hs.append(deepcopy(harmony))

    def add_measure(self, part_index: int, measure: Measure | None = None) -> None:
        self._begin()
        part = self.score.parts[part_index]
        number = len(part.measures) + 1
        part.measures.append(deepcopy(measure) if measure else Measure(number))

    def remove_measure(self, part_index: int, measure_index: int) -> Measure:
        self._begin()
        return self.score.parts[part_index].measures.pop(measure_index)
