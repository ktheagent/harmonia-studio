from __future__ import annotations
from copy import deepcopy
from collections import defaultdict
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch
from harmonia_studio.harmony.styles import harmonize_style
from harmonia_studio.harmony.satb import QUALITY_INTERVALS
from .templates import EnsembleTemplate, get_template

def _fit_pitch(midi:int,lo:int,hi:int)->int:
    candidates=[midi+12*k for k in range(-8,9) if lo<=midi+12*k<=hi]
    if candidates:
        center=(lo+hi)/2
        return min(candidates,key=lambda x:abs(x-center))
    return max(lo,min(hi,midi))

def auto_arrange(score:Score,template:EnsembleTemplate|str,style_id:str="pop",complexity:str="balanced")->Score:
    if isinstance(template,str):
        template=get_template(template)
    if not score.parts:
        return Score(score.title,score.composer,[],{**score.metadata,"ensemble":template.name})
    styled=harmonize_style(score,style_id,complexity)
    plan=styled.plan
    source=score.parts[0]
    max_measures=len(source.measures)
    by_measure=defaultdict(list)
    for c in plan.choices: by_measure[c.measure_index].append(c)
    parts=[]
    for spec in template.instruments:
        measures=[
            Measure(i+1,time=deepcopy(source.measures[i].time),key=deepcopy(source.measures[i].key),tempo=source.measures[i].tempo)
            for i in range(max_measures)
        ]
        if spec.role=="melody":
            for mi,sm in enumerate(source.measures):
                for n in sm.notes:
                    if n.pitch is None:
                        measures[mi].notes.append(deepcopy(n)); continue
                    concert=_fit_pitch(n.pitch.midi(),spec.low,spec.high)
                    measures[mi].notes.append(Note(Pitch.from_midi(concert),n.duration,n.voice,n.staff,n.dots,n.tie_start,n.tie_stop,
                        list(n.articulations),n.dynamic,deepcopy(n.lyrics),n.velocity,n.onset))
        else:
            for mi in range(max_measures):
                for c in by_measure.get(mi,[]):
                    intervals=QUALITY_INTERVALS.get(c.quality,(0,4,7))
                    pcs=[(c.root_pc+x)%12 for x in intervals]
                    duration=max(.25,measures[mi].time.beats*4.0/measures[mi].time.beat_type-c.onset)
                    if spec.role=="bass":
                        candidates=[m for m in range(spec.low,spec.high+1) if m%12==c.root_pc]
                        pitch=min(candidates,key=lambda x:abs(x-(spec.low+spec.high)/2)) if candidates else _fit_pitch(36+c.root_pc,spec.low,spec.high)
                        measures[mi].notes.append(Note(Pitch.from_midi(pitch),duration,onset=c.onset,velocity=86))
                    else:
                        max_notes=min(max(1,spec.polyphony),4)
                        center=(spec.low+spec.high)//2
                        selected=[]
                        for pc in pcs:
                            cand=[m for m in range(spec.low,spec.high+1) if m%12==pc]
                            if cand:
                                selected.append(min(cand,key=lambda x:abs(x-center)))
                        selected=sorted(set(selected))[:max_notes]
                        for p in selected:
                            measures[mi].notes.append(Note(Pitch.from_midi(p),duration,onset=c.onset,velocity=72 if spec.role=="harmony" else 68))
        parts.append(Part(spec.id,spec.name,Instrument(spec.name,spec.midi_program,spec.transposition),measures))
    return Score(score.title,score.composer,parts,{
        **deepcopy(score.metadata),
        "ensemble":template.name,
        "arrangementStyle":style_id,
        "arrangementComplexity":complexity,
    })
