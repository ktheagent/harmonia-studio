from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event, Lock
import time
from typing import Callable
from .score import Score, Note

class PlaybackState(str, Enum):
    STOPPED="stopped"
    PLAYING="playing"
    PAUSED="paused"

@dataclass(frozen=True)
class PlaybackEvent:
    time_seconds: float
    duration_seconds: float
    midi: int
    velocity: int
    part_index: int
    measure_index: int

class PlaybackEngine:
    def __init__(self, sink: Callable[[PlaybackEvent], None] | None = None):
        self.state=PlaybackState.STOPPED
        self.tempo_factor=1.0
        self.loop_range: tuple[int,int] | None=None
        self.muted:set[int]=set()
        self.soloed:set[int]=set()
        self.volumes:dict[int,float]={}
        self.cursor_measure=0
        self._stop=Event()
        self._pause=Event()
        self._thread:Thread|None=None
        self._sink=sink or (lambda event: None)
        self._lock=Lock()

    def schedule(self, score:Score)->list[PlaybackEvent]:
        events=[]
        for pi,part in enumerate(score.parts):
            if pi in self.muted or (self.soloed and pi not in self.soloed):
                continue
            absolute_quarters=0.0
            for mi,measure in enumerate(part.measures):
                if self.loop_range and not (self.loop_range[0] <= mi <= self.loop_range[1]):
                    absolute_quarters += measure.time.beats*4.0/measure.time.beat_type
                    continue
                bpm=max(1.0,measure.tempo)*self.tempo_factor
                sec_per_quarter=60.0/bpm
                volume=max(0.0,min(1.0,self.volumes.get(pi,1.0)))
                for note in measure.notes:
                    if note.pitch is not None:
                        events.append(PlaybackEvent(
                            (absolute_quarters+note.onset)*sec_per_quarter,
                            note.duration*sec_per_quarter,
                            note.pitch.midi(),
                            int(note.velocity*volume),
                            pi,mi
                        ))
                absolute_quarters += measure.time.beats*4.0/measure.time.beat_type
        events.sort(key=lambda e:(e.time_seconds,e.part_index,e.midi))
        if events and self.loop_range:
            start=min(e.time_seconds for e in events)
            events=[PlaybackEvent(e.time_seconds-start,e.duration_seconds,e.midi,e.velocity,e.part_index,e.measure_index) for e in events]
        return events

    def play(self, score:Score)->None:
        self.stop()
        events=self.schedule(score)
        self._stop.clear(); self._pause.clear()
        self.state=PlaybackState.PLAYING
        def run():
            start=time.monotonic()
            paused_total=0.0
            pause_started=None
            for event in events:
                while not self._stop.is_set():
                    if self._pause.is_set():
                        if pause_started is None: pause_started=time.monotonic()
                        time.sleep(0.01); continue
                    if pause_started is not None:
                        paused_total += time.monotonic()-pause_started
                        pause_started=None
                    elapsed=time.monotonic()-start-paused_total
                    remaining=event.time_seconds-elapsed
                    if remaining<=0: break
                    time.sleep(min(0.01,remaining))
                if self._stop.is_set(): break
                self.cursor_measure=event.measure_index
                self._sink(event)
            with self._lock:
                if not self._stop.is_set():
                    self.state=PlaybackState.STOPPED
        self._thread=Thread(target=run,daemon=True)
        self._thread.start()

    def pause(self)->None:
        if self.state==PlaybackState.PLAYING:
            self._pause.set(); self.state=PlaybackState.PAUSED

    def resume(self)->None:
        if self.state==PlaybackState.PAUSED:
            self._pause.clear(); self.state=PlaybackState.PLAYING

    def stop(self)->None:
        self._stop.set(); self._pause.clear(); self.state=PlaybackState.STOPPED
        self._thread=None

    def seek_measure(self, measure_index:int)->None:
        self.cursor_measure=max(0,int(measure_index))

    def set_loop(self,start_measure:int|None,end_measure:int|None=None)->None:
        self.loop_range=None if start_measure is None else (start_measure, end_measure if end_measure is not None else start_measure)

    def mute(self,part_index:int,value:bool=True)->None:
        self.muted.add(part_index) if value else self.muted.discard(part_index)

    def solo(self,part_index:int,value:bool=True)->None:
        self.soloed.add(part_index) if value else self.soloed.discard(part_index)

    def set_volume(self,part_index:int,volume:float)->None:
        self.volumes[part_index]=max(0.0,min(1.0,float(volume)))
