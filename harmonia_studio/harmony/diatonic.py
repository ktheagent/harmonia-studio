from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from collections import defaultdict
from harmonia_studio.score import Score, Harmony
from harmonia_studio.analysis.tonal import analyze_tonality, NAMES

MAJOR_TRIADS={0:("major",{0,4,7}),2:("minor",{0,3,7}),4:("minor",{0,3,7}),5:("major",{0,4,7}),7:("major",{0,4,7}),9:("minor",{0,3,7}),11:("diminished",{0,3,6})}
MINOR_TRIADS={0:("minor",{0,3,7}),2:("diminished",{0,3,6}),3:("major",{0,4,7}),5:("minor",{0,3,7}),7:("major",{0,4,7}),8:("major",{0,4,7}),10:("major",{0,4,7})}

@dataclass(frozen=True)
class HarmonyChoice:
    measure_index:int
    onset:float
    root_pc:int
    root_name:str
    quality:str
    inversion:int=0
    score:float=0.0

@dataclass
class HarmonyPlan:
    key:str
    mode:str
    choices:list[HarmonyChoice]
    preserve_melody:bool=True

def _transition_bonus(prev_rel:int|None,cur_rel:int)->float:
    if prev_rel is None: return 0.0
    favored={(0,5),(5,7),(7,0),(0,9),(9,2),(2,7),(4,9),(11,0)}
    return 0.7 if (prev_rel,cur_rel) in favored else 0.0

def harmonize_diatonic(score:Score, harmonic_density:str="measure")->HarmonyPlan:
    tonal=analyze_tonality(score)
    tonic=NAMES.index(tonal.global_key.tonic)
    triads=MAJOR_TRIADS if tonal.global_key.mode=="major" else MINOR_TRIADS
    melody=score.parts[0] if score.parts else None
    if not melody:
        return HarmonyPlan(tonal.global_key.tonic,tonal.global_key.mode,[])
    choices=[]
    prev_rel=None
    total=len(melody.measures)
    for mi,m in enumerate(melody.measures):
        events=[]
        if harmonic_density=="beat":
            grouped=defaultdict(list)
            for n in m.notes:
                if n.pitch is not None: grouped[round(n.onset,3)].append(n)
            events=[(o,ns) for o,ns in sorted(grouped.items())]
        else:
            events=[(0.0,[n for n in m.notes if n.pitch is not None])]
        for onset,notes in events:
            if not notes: continue
            weighted=defaultdict(float)
            for n in notes: weighted[n.pitch.midi()%12]+=max(.125,n.duration)
            candidates=[]
            for rel,(quality,intervals) in triads.items():
                root=(tonic+rel)%12
                pcs={(root+i)%12 for i in intervals}
                coverage=sum(w for pc,w in weighted.items() if pc in pcs)
                non=sum(w for pc,w in weighted.items() if pc not in pcs)
                scorev=coverage*2.0-non*1.2+_transition_bonus(prev_rel,rel)
                # cadence bias at the end
                if mi==total-1 and rel==0: scorev+=2.0
                if mi==total-2 and rel==7: scorev+=1.0
                candidates.append((scorev,rel,root,quality))
            candidates.sort(reverse=True)
            scorev,rel,root,quality=candidates[0]
            choices.append(HarmonyChoice(mi,onset,root,NAMES[root],quality,0,scorev))
            prev_rel=rel
    return HarmonyPlan(tonal.global_key.tonic,tonal.global_key.mode,choices,True)

def apply_harmony_plan(score:Score,plan:HarmonyPlan)->Score:
    out=deepcopy(score)
    by_measure=defaultdict(list)
    for c in plan.choices:
        suffix={"major":"","minor":"m","diminished":"dim"}.get(c.quality,c.quality)
        by_measure[c.measure_index].append(Harmony(c.root_name,c.quality,"",c.root_name+suffix))
    if out.parts:
        for mi,m in enumerate(out.parts[0].measures):
            m.harmonies=by_measure.get(mi,[])
    return out
