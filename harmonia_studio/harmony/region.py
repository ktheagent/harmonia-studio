from __future__ import annotations
from copy import deepcopy
from collections import defaultdict
from harmonia_studio.score import Score, Harmony
from .styles import harmonize_style

def reharmonize_region(score:Score,start_measure:int,end_measure:int,style_id:str,complexity:str="balanced")->Score:
    if start_measure<0 or end_measure<start_measure:
        raise ValueError("Invalid measure range")
    out=deepcopy(score)
    if not out.parts:
        return out
    result=harmonize_style(score,style_id,complexity)
    by_measure=defaultdict(list)
    for c in result.plan.choices:
        if start_measure<=c.measure_index<=end_measure:
            suffix={
                "major":"","minor":"m","diminished":"dim","dominant-seventh":"7",
                "major-seventh":"maj7","minor-seventh":"m7"
            }.get(c.quality,c.quality)
            by_measure[c.measure_index].append(Harmony(c.root_name,c.quality,"",c.root_name+suffix))
    for mi in range(start_measure,min(end_measure+1,len(out.parts[0].measures))):
        out.parts[0].measures[mi].harmonies=by_measure.get(mi,[])
    out.metadata={**out.metadata,"lastReharmonizedRegion":[start_measure,end_measure],"lastHarmonyStyle":style_id}
    return out
