from __future__ import annotations
from dataclasses import dataclass, field, asdict
from fractions import Fraction
from typing import Any

@dataclass
class Pitch:
    step: str
    octave: int
    alter: int = 0
    def midi(self) -> int:
        pc={"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}[self.step.upper()] + self.alter
        return 12*(self.octave+1)+pc
    @classmethod
    def from_midi(cls, n:int)->"Pitch":
        names=[("C",0),("C",1),("D",0),("D",1),("E",0),("F",0),("F",1),("G",0),("G",1),("A",0),("A",1),("B",0)]
        step,alter=names[n%12]
        return cls(step,n//12-1,alter)

@dataclass
class Lyric:
    text: str
    syllabic: str = ""

@dataclass
class Note:
    pitch: Pitch | None = None
    duration: float = 1.0
    voice: int = 1
    staff: int = 1
    dots: int = 0
    tie_start: bool = False
    tie_stop: bool = False
    articulations: list[str] = field(default_factory=list)
    dynamic: str = ""
    lyrics: list[Lyric] = field(default_factory=list)
    velocity: int = 80
    onset: float = 0.0
    @property
    def is_rest(self)->bool: return self.pitch is None

@dataclass
class Harmony:
    root: str
    kind: str = "major"
    bass: str = ""
    symbol: str = ""

@dataclass
class TimeSignature:
    beats: int = 4
    beat_type: int = 4

@dataclass
class KeySignature:
    fifths: int = 0
    mode: str = "major"

@dataclass
class Measure:
    number: int
    notes: list[Note] = field(default_factory=list)
    harmonies: list[Harmony] = field(default_factory=list)
    time: TimeSignature = field(default_factory=TimeSignature)
    key: KeySignature = field(default_factory=KeySignature)
    tempo: float = 120.0
    repeat_start: bool = False
    repeat_end: bool = False
    rehearsal_mark: str = ""

@dataclass
class Instrument:
    name: str = "Piano"
    midi_program: int = 0
    transposition: int = 0

@dataclass
class Part:
    id: str
    name: str
    instrument: Instrument = field(default_factory=Instrument)
    measures: list[Measure] = field(default_factory=list)

@dataclass
class Score:
    title: str = "Untitled"
    composer: str = ""
    parts: list[Part] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def iter_notes(self):
        for part in self.parts:
            for measure in part.measures:
                yield from measure.notes

    def to_dict(self)->dict:
        return asdict(self)

    @classmethod
    def from_dict(cls,data:dict)->"Score":
        parts=[]
        for pd in data.get("parts",[]):
            inst=Instrument(**pd.get("instrument",{}))
            measures=[]
            for md in pd.get("measures",[]):
                notes=[]
                for nd in md.get("notes",[]):
                    pitch=Pitch(**nd["pitch"]) if nd.get("pitch") else None
                    lyrics=[Lyric(**x) for x in nd.get("lyrics",[])]
                    nn={k:v for k,v in nd.items() if k not in {"pitch","lyrics"}}
                    notes.append(Note(pitch=pitch,lyrics=lyrics,**nn))
                harmonies=[Harmony(**x) for x in md.get("harmonies",[])]
                time=TimeSignature(**md.get("time",{}))
                key=KeySignature(**md.get("key",{}))
                mm={k:v for k,v in md.items() if k not in {"notes","harmonies","time","key"}}
                measures.append(Measure(notes=notes,harmonies=harmonies,time=time,key=key,**mm))
            parts.append(Part(id=pd["id"],name=pd.get("name",pd["id"]),instrument=inst,measures=measures))
        return cls(title=data.get("title","Untitled"),composer=data.get("composer",""),parts=parts,metadata=dict(data.get("metadata",{})))
