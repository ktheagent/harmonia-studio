from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch
from .diatonic import HarmonyPlan, HarmonyChoice, harmonize_diatonic
from .voice_leading import DEFAULT_RANGES

QUALITY_INTERVALS={
    "major":(0,4,7),
    "minor":(0,3,7),
    "diminished":(0,3,6),
    "augmented":(0,4,8),
    "dominant-seventh":(0,4,7,10),
    "major-seventh":(0,4,7,11),
    "minor-seventh":(0,3,7,10),
}

@dataclass
class SATBOptions:
    ranges:dict[str,tuple[int,int]]=field(default_factory=lambda:dict(DEFAULT_RANGES))
    position:str="closed"  # closed/open
    doubling:str="root"
    melody_voice:str="soprano"
    bass_movement:str="smooth"
    max_upper_interval:int=12

def _candidates_for_pc(pc:int,lo:int,hi:int)->list[int]:
    return [m for m in range(lo,hi+1) if m%12==pc]

def _nearest(candidates:list[int],target:int,below:int|None=None,above:int|None=None)->int|None:
    xs=[x for x in candidates if (below is None or x<below) and (above is None or x>above)]
    if not xs: return None
    return min(xs,key=lambda x:abs(x-target))

def _pick_chord_tone(pcs:set[int],lo:int,hi:int,target:int,below:int|None=None,above:int|None=None,avoid:set[int]|None=None)->int:
    avoid=avoid or set()
    candidates=[m for m in range(lo,hi+1) if m%12 in pcs and m not in avoid and (below is None or m<below) and (above is None or m>above)]
    if not candidates:
        candidates=[m for m in range(lo,hi+1) if m%12 in pcs and (below is None or m<below) and (above is None or m>above)]
    if not candidates:
        candidates=[max(lo,min(hi,target))]
    return min(candidates,key=lambda x:abs(x-target))

def _melody_pitch_for_choice(m:Measure,onset:float,range_:tuple[int,int])->int:
    notes=[n for n in m.notes if n.pitch is not None]
    if notes:
        n=min(notes,key=lambda x:abs(x.onset-onset))
        return n.pitch.midi()
    lo,hi=range_
    return max(lo,min(hi,72))

def harmonize_satb(score:Score,plan:HarmonyPlan|None=None,options:SATBOptions|None=None)->Score:
    if not score.parts:
        return Score(score.title,score.composer,[],deepcopy(score.metadata))
    o=options or SATBOptions()
    if o.melody_voice!="soprano":
        raise ValueError("MVP SATB generator currently requires soprano melody")
    plan=plan or harmonize_diatonic(score)
    melody=deepcopy(score.parts[0])
    melody.id="S"; melody.name="Soprano"; melody.instrument=Instrument("Voice",52)

    max_measures=len(melody.measures)
    alto=[Measure(i+1,time=deepcopy(melody.measures[i].time),key=deepcopy(melody.measures[i].key),tempo=melody.measures[i].tempo) for i in range(max_measures)]
    tenor=[deepcopy(m) for m in alto]
    bass=[deepcopy(m) for m in alto]
    for m in tenor: m.notes=[]; m.harmonies=[]
    for m in bass: m.notes=[]; m.harmonies=[]
    for m in alto: m.notes=[]; m.harmonies=[]

    prev={"alto":64,"tenor":55,"bass":48}
    for choice in plan.choices:
        if choice.measure_index>=max_measures: continue
        src=melody.measures[choice.measure_index]
        intervals=QUALITY_INTERVALS.get(choice.quality,(0,4,7))
        pcs={(choice.root_pc+i)%12 for i in intervals}
        sop=_melody_pitch_for_choice(src,choice.onset,o.ranges["soprano"])
        # If melody is a non-chord tone, preserve it and harmonize beneath.
        blo,bhi=o.ranges["bass"]
        bass_pc=choice.root_pc
        if choice.inversion and choice.inversion < len(intervals):
            bass_pc=(choice.root_pc+intervals[choice.inversion])%12
        root_candidates=_candidates_for_pc(bass_pc,blo,bhi)
        if o.bass_movement=="smooth" and root_candidates:
            b=_nearest(root_candidates,prev["bass"]) or root_candidates[0]
        else:
            b=min(root_candidates,key=lambda x:abs(x-48)) if root_candidates else _pick_chord_tone(pcs,blo,bhi,48)
        tlo,thi=o.ranges["tenor"]; alo,ahi=o.ranges["alto"]
        t=_pick_chord_tone(pcs,tlo,thi,prev["tenor"],below=sop,above=b)
        a=_pick_chord_tone(pcs,alo,ahi,prev["alto"],below=sop,above=t)
        # Repair order if necessary with target reselection.
        if not (b<t<a<sop):
            t=_pick_chord_tone(pcs,tlo,thi,55,below=sop,above=b)
            a=_pick_chord_tone(pcs,alo,ahi,64,below=sop,above=t)
        measure_len=src.time.beats*4.0/src.time.beat_type
        duration=max(0.25,measure_len-choice.onset)
        alto[choice.measure_index].notes.append(Note(Pitch.from_midi(a),duration,onset=choice.onset))
        tenor[choice.measure_index].notes.append(Note(Pitch.from_midi(t),duration,onset=choice.onset))
        bass[choice.measure_index].notes.append(Note(Pitch.from_midi(b),duration,onset=choice.onset))
        prev.update(alto=a,tenor=t,bass=b)

    parts=[
        melody,
        Part("A","Alto",Instrument("Voice",52),alto),
        Part("T","Tenor",Instrument("Voice",52),tenor),
        Part("B","Bass",Instrument("Voice",52),bass),
    ]
    return Score(score.title,score.composer,parts,{**deepcopy(score.metadata),"arrangement":"SATB","harmonyKey":plan.key})
