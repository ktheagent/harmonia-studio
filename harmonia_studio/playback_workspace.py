from __future__ import annotations

from .playback import PlaybackEvent


def note_tag(event: PlaybackEvent) -> str:
    return f"note:{event.part_index}:{event.measure_index}:{event.note_index}"


def measure_tag(measure_index: int) -> str:
    return f"measure:{max(0, int(measure_index))}"


def parse_measure_value(value: str | int, measure_count: int) -> int:
    if measure_count <= 0:
        return 0
    try:
        index = int(value) - 1
    except (TypeError, ValueError):
        index = 0
    return max(0, min(measure_count - 1, index))
