from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from harmonia_studio.score import Score
from .functions import analyze_functional_harmony, FunctionalChord

@dataclass(frozen=True)
class Cadence:
    measure_index:int
    kind:str
    confidence:float

@dataclass
class PhraseAnalysis:
    phrase_boundaries:list[int]
    cadences:list[Cadence]
    repeated_motifs:list[tuple[int,int]]
    sections:list[tuple[int,int]]

def classify_cadence(previous:FunctionalChord|None,current:FunctionalChord|None,measure_index:int)->Cadence|None:
    if not previous or not current:
        return None
    a=previous.roman; b=current.roman
    if a.startswith("V") and b in {"I","i"}:
        kind="authentic" if previous.chord.inversion in {0,-1} and current.chord.inversion in {0,-1} else "imperfect"
        return Cadence(measure_index,kind,0.9)
    if a in {"IV","iv"} and b in {"I","i"}:
        return Cadence(measure_index,"plagal",0.85)
    if a.startswith("V") and b in {"vi","VI"}:
        return Cadence(measure_index,"deceptive",0.85)
    if b=="V":
        return Cadence(measure_index,"half",0.75)
    return None

def _motif_signature(score:Score,measure_index:int)->tuple[int,...]:
    pitches=[]
    for p in score.parts[:1]:
        if measure_index < len(p.measures):
            pitches=[n.pitch.midi() for n in p.measures[measure_index].notes if n.pitch is not None]
    if len(pitches)<2: return tuple(pitches)
    return tuple(pitches[i+1]-pitches[i] for i in range(len(pitches)-1))

def analyze_phrases(score:Score,phrase_length:int=4)->PhraseAnalysis:
    max_measures=max((len(p.measures) for p in score.parts),default=0)
    if max_measures==0:
        return PhraseAnalysis([],[],[],[])
    funcs=analyze_functional_harmony(score)
    by_measure=defaultdict(list)
    for f in funcs: by_measure[f.chord.measure_index].append(f)

    boundaries=[]
    cadences=[]
    for mi in range(max_measures):
        is_boundary=((mi+1)%max(1,phrase_length)==0) or mi==max_measures-1
        if is_boundary:
            boundaries.append(mi)
            cur=by_measure.get(mi,[])
            prev=by_measure.get(mi-1,[]) if mi>0 else []
            prev_chord=prev[-1] if prev else (cur[-2] if len(cur)>=2 else None)
            cur_chord=cur[-1] if cur else None
            c=classify_cadence(prev_chord,cur_chord,mi)
            if c: cadences.append(c)

    signatures={}
    repetitions=[]
    for mi in range(max_measures):
        sig=_motif_signature(score,mi)
        if len(sig)>=1:
            if sig in signatures:
                repetitions.append((signatures[sig],mi))
            else:
                signatures[sig]=mi

    starts=[0]+[b+1 for b in boundaries[:-1]]
    sections=[(s,b) for s,b in zip(starts,boundaries)]
    return PhraseAnalysis(boundaries,cadences,repetitions,sections)
