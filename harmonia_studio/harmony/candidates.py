from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from .styles import harmonize_style, StyleResult, get_style
from .diatonic import HarmonyPlan, HarmonyChoice
from .satb import harmonize_satb
from .voice_leading import validate_voice_leading
from harmonia_studio.analysis.tonal import NAMES
from harmonia_studio.score import Score

@dataclass
class HarmonyCandidate:
    id:str
    label:str
    mode:str
    result:StyleResult
    quality_score:float

def _quality(warnings)->float:
    penalty=0.0
    for w in warnings:
        penalty += 7 if w.severity=="error" else 2
    return max(0.0, min(100.0, 100.0-penalty))

def _distinct_plan(plan:HarmonyPlan, mode:str)->HarmonyPlan:
    out=deepcopy(plan)
    choices=list(out.choices)
    if not choices:
        return out
    tonic=NAMES.index(out.key)
    if mode=="stylistic" and len(choices)>1:
        c=choices[1]
        choices[1]=HarmonyChoice(c.measure_index,c.onset,c.root_pc,c.root_name,c.quality,1,c.score)
    elif mode=="creative":
        # Add a dominant push before the ending and an inversion earlier.
        if len(choices)>1:
            idx=max(0,len(choices)-2); c=choices[idx]
            root=(tonic+7)%12
            choices[idx]=HarmonyChoice(c.measure_index,c.onset,root,NAMES[root],"dominant-seventh",0,c.score)
        if len(choices)>2:
            c=choices[1]
            choices[1]=HarmonyChoice(c.measure_index,c.onset,c.root_pc,c.root_name,c.quality,1,c.score)
    out.choices=choices
    return out

def generate_candidates(score:Score,style_id:str)->list[HarmonyCandidate]:
    modes=[("A","Conservative","conservative"),("B","Stylistic","stylistic"),("C","Creative","creative")]
    out=[]
    seen=set()
    for cid,label,mode in modes:
        base=harmonize_style(score,style_id,mode)
        plan=_distinct_plan(base.plan,mode)
        arranged=harmonize_satb(score,plan)
        warnings=validate_voice_leading(arranged)
        result=StyleResult(get_style(style_id),plan,arranged,warnings)
        sig=tuple((c.root_pc,c.quality,c.inversion) for c in plan.choices)
        if sig in seen and plan.choices:
            # Last-resort deterministic differentiation: change first inversion.
            c=plan.choices[0]
            plan.choices[0]=HarmonyChoice(c.measure_index,c.onset,c.root_pc,c.root_name,c.quality,(c.inversion+1)%2,c.score)
            arranged=harmonize_satb(score,plan)
            warnings=validate_voice_leading(arranged)
            result=StyleResult(get_style(style_id),plan,arranged,warnings)
            sig=tuple((c.root_pc,c.quality,c.inversion) for c in plan.choices)
        seen.add(sig)
        out.append(HarmonyCandidate(cid,label,mode,result,_quality(warnings)))
    return out
