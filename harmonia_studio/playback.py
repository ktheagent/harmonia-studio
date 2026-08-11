from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Event, Lock, Thread, current_thread
import time
from typing import Callable

from .score import Score


class PlaybackState(str, Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass(frozen=True)
class PlaybackEvent:
    time_seconds: float
    duration_seconds: float
    midi: int
    velocity: int
    part_index: int
    measure_index: int
    note_index: int = 0


class PlaybackEngine:
    """Threaded score transport.

    The engine schedules score events and emits them to ``sink``.  It does not
    itself open an audio device; callers can use the sink for visual playback,
    MIDI, synthesis, or another output backend.
    """

    def __init__(self, sink: Callable[[PlaybackEvent], None] | None = None):
        self.state = PlaybackState.STOPPED
        self.tempo_factor = 1.0
        self.loop_range: tuple[int, int] | None = None
        self.muted: set[int] = set()
        self.soloed: set[int] = set()
        self.volumes: dict[int, float] = {}
        self.cursor_measure = 0

        self._stop = Event()
        self._pause = Event()
        self._thread: Thread | None = None
        self._sink = sink or (lambda event: None)
        self._lock = Lock()

    def schedule(self, score: Score, start_measure: int | None = None) -> list[PlaybackEvent]:
        """Build a time-ordered event schedule.

        Timing is accumulated measure-by-measure so tempo changes do not
        retroactively alter elapsed time from earlier measures.
        """
        events: list[PlaybackEvent] = []
        measure_starts: dict[int, float] = {}

        for pi, part in enumerate(score.parts):
            if pi in self.muted or (self.soloed and pi not in self.soloed):
                continue

            absolute_seconds = 0.0
            for mi, measure in enumerate(part.measures):
                measure_starts[mi] = min(measure_starts.get(mi, absolute_seconds), absolute_seconds)
                bpm = max(1.0, float(measure.tempo)) * max(0.01, float(self.tempo_factor))
                seconds_per_quarter = 60.0 / bpm
                volume = max(0.0, min(1.0, self.volumes.get(pi, 1.0)))

                include_measure = True
                if start_measure is not None and mi < start_measure:
                    include_measure = False
                if self.loop_range is not None:
                    loop_start, loop_end = self.loop_range
                    if not (loop_start <= mi <= loop_end):
                        include_measure = False

                if include_measure:
                    for ni, note in enumerate(measure.notes):
                        if note.pitch is None:
                            continue
                        events.append(
                            PlaybackEvent(
                                absolute_seconds + float(note.onset) * seconds_per_quarter,
                                float(note.duration) * seconds_per_quarter,
                                note.pitch.midi(),
                                int(max(0, min(127, round(note.velocity * volume)))),
                                pi,
                                mi,
                                ni,
                            )
                        )

                measure_quarters = float(measure.time.beats) * 4.0 / max(1, int(measure.time.beat_type))
                absolute_seconds += measure_quarters * seconds_per_quarter

        events.sort(key=lambda e: (e.time_seconds, e.part_index, e.measure_index, e.note_index, e.midi))
        if not events:
            return events

        if self.loop_range is not None:
            origin_measure = self.loop_range[0]
        elif start_measure is not None:
            origin_measure = max(0, int(start_measure))
        else:
            origin_measure = 0

        origin = measure_starts.get(origin_measure)
        if origin is None:
            origin = min(e.time_seconds for e in events)

        if origin:
            events = [
                PlaybackEvent(
                    max(0.0, e.time_seconds - origin),
                    e.duration_seconds,
                    e.midi,
                    e.velocity,
                    e.part_index,
                    e.measure_index,
                    e.note_index,
                )
                for e in events
            ]
        return events

    def play(self, score: Score, start_measure: int | None = None) -> None:
        self.stop()
        start = self.cursor_measure if start_measure is None else max(0, int(start_measure))
        self.cursor_measure = start
        events = self.schedule(score, start_measure=start)
        self._stop.clear()
        self._pause.clear()

        if not events:
            self.state = PlaybackState.STOPPED
            return

        self.state = PlaybackState.PLAYING

        def run() -> None:
            try:
                while not self._stop.is_set():
                    completed = self._play_once(events)
                    if not completed or self.loop_range is None:
                        break
            finally:
                with self._lock:
                    if not self._stop.is_set():
                        self.state = PlaybackState.STOPPED
                    if self._thread is current_thread():
                        self._thread = None

        thread = Thread(target=run, daemon=True, name="harmonia-playback")
        self._thread = thread
        thread.start()

    def _play_once(self, events: list[PlaybackEvent]) -> bool:
        start = time.monotonic()
        paused_total = 0.0
        pause_started: float | None = None

        for event in events:
            while not self._stop.is_set():
                if self._pause.is_set():
                    if pause_started is None:
                        pause_started = time.monotonic()
                    time.sleep(0.01)
                    continue

                if pause_started is not None:
                    paused_total += time.monotonic() - pause_started
                    pause_started = None

                elapsed = time.monotonic() - start - paused_total
                remaining = event.time_seconds - elapsed
                if remaining <= 0:
                    break
                time.sleep(min(0.01, remaining))

            if self._stop.is_set():
                return False

            self.cursor_measure = event.measure_index
            self._sink(event)

        return True

    def pause(self) -> None:
        if self.state == PlaybackState.PLAYING:
            self._pause.set()
            self.state = PlaybackState.PAUSED

    def resume(self) -> None:
        if self.state == PlaybackState.PAUSED:
            self._pause.clear()
            self.state = PlaybackState.PLAYING

    def stop(self) -> None:
        self._stop.set()
        self._pause.clear()

        thread = self._thread
        self._thread = None
        self.state = PlaybackState.STOPPED

        if thread is not None and thread.is_alive() and thread is not current_thread():
            thread.join(timeout=0.25)

    def seek_measure(self, measure_index: int) -> None:
        self.cursor_measure = max(0, int(measure_index))

    def set_loop(
        self,
        start_measure: int | None,
        end_measure: int | None = None,
    ) -> None:
        if start_measure is None:
            self.loop_range = None
            return
        start = max(0, int(start_measure))
        end = start if end_measure is None else max(0, int(end_measure))
        if end < start:
            start, end = end, start
        self.loop_range = (start, end)

    def mute(self, part_index: int, value: bool = True) -> None:
        if value:
            self.muted.add(part_index)
        else:
            self.muted.discard(part_index)

    def solo(self, part_index: int, value: bool = True) -> None:
        if value:
            self.soloed.add(part_index)
        else:
            self.soloed.discard(part_index)

    def set_volume(self, part_index: int, volume: float) -> None:
        self.volumes[part_index] = max(0.0, min(1.0, float(volume)))
