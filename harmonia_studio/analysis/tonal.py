from __future__ import annotations
from dataclasses import dataclass
import math
from harmonia_studio.score import Score, Measure

MAJOR_PROFILE=[6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]
MINOR_PROFILE=[6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17]
NAMES=["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]

@dataclass(frozen=True)
class KeyEstimate:
    tonic: str
    mode: str
    confidence: float
    score: float

@dataclass
class TonalAnalysis:
    global_key: KeyEstimate
    local_keys: list[KeyEstimate]
    modulation_candidates: list[tuple[int,KeyEstimate]]
    pitch_class_weights: list[float]

def _weights_from_notes(notes):
    w=[0.0]*12
    for n in notes:
        if n.pitch is not None:
            w[n.pitch.midi()%12]+=max(0.125,float(n.duration))
    return w

def _cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na and nb else 0.0

def estimate_key_from_weights(weights)->KeyEstimate:
    candidates=[]
    for tonic in range(12):
        for mode,profile in [("major",MAJOR_PROFILE),("minor",MINOR_PROFILE)]:
            rotated=[profile[(pc-tonic)%12] for pc in range(12)]
            candidates.append((_cosine(weights,rotated),tonic,mode))
    candidates.sort(reverse=True)
    best=candidates[0]
    second=candidates[1][0] if len(candidates)>1 else 0
    confidence=max(0.0,min(1.0,(best[0]-second+0.05)/0.25))
    return KeyEstimate(NAMES[best[1]],best[2],confidence,best[0])

def analyze_tonality(score:Score)->TonalAnalysis:
    all_notes=list(score.iter_notes())
    weights=_weights_from_notes(all_notes)
    global_key=estimate_key_from_weights(weights)
    max_measures=max((len(p.measures) for p in score.parts),default=0)
    locals=[]; mods=[]
    for mi in range(max_measures):
        notes=[]
        for p in score.parts:
            if mi < len(p.measures): notes.extend(p.measures[mi].notes)
        est=estimate_key_from_weights(_weights_from_notes(notes)) if notes else global_key
        locals.append(est)
        if (est.tonic,est.mode)!=(global_key.tonic,global_key.mode) and est.confidence>=0.2:
            mods.append((mi,est))
    return TonalAnalysis(global_key,locals,mods,weights)

def scale_pitch_classes(key:KeyEstimate)->set[int]:
    tonic=NAMES.index(key.tonic)
    pattern=[0,2,4,5,7,9,11] if key.mode=="major" else [0,2,3,5,7,8,10]
    return {(tonic+x)%12 for x in pattern}
