from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from harmonia_studio.score import Score, Harmony

NAMES_SHARP=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
TEMPLATES={
    "major": {0,4,7},
    "minor": {0,3,7},
    "diminished": {0,3,6},
    "augmented": {0,4,8},
    "dominant-seventh": {0,4,7,10},
    "major-seventh": {0,4,7,11},
    "minor-seventh": {0,3,7,10},
    "half-diminished": {0,3,6,10},
    "diminished-seventh": {0,3,6,9},
    "sus2": {0,2,7},
    "sus4": {0,5,7},
    "sixth": {0,4,7,9},
    "minor-sixth": {0,3,7,9},
}
SUFFIX={
    "major":"","minor":"m","diminished":"dim","augmented":"aug",
    "dominant-seventh":"7","major-seventh":"maj7","minor-seventh":"m7",
    "half-diminished":"m7b5","diminished-seventh":"dim7","sus2":"sus2",
    "sus4":"sus4","sixth":"6","minor-sixth":"m6"
}

@dataclass(frozen=True)
class DetectedChord:
    measure_index:int
    onset:float
    root:int
    root_name:str
    quality:str
    bass:int
    bass_name:str
    inversion:int
    extensions:tuple[int,...]=()
    alterations:tuple[str,...]=()
    confidence:float=0.0
    symbol:str=""
    duration:float=0.0

def _score_template(pcs:set[int], root:int, template:set[int])->float:
    rel={(p-root)%12 for p in pcs}
    hits=len(rel & template)
    missing=len(template-rel)
    extras=len(rel-template)
    root_bonus=0.5 if 0 in rel else -0.75
    return hits*1.4 - missing*1.0 - extras*0.55 + root_bonus

def detect_pitch_class_chord(midi_notes:list[int], measure_index:int=0, onset:float=0.0)->DetectedChord|None:
    if not midi_notes:
        return None
    pcs={n%12 for n in midi_notes}
    bass=min(midi_notes)%12
    candidates=[]
    for root in range(12):
        for quality,template in TEMPLATES.items():
            score=_score_template(pcs,root,template)
            candidates.append((score,root,quality))
    candidates.sort(reverse=True)
    score,root,quality=candidates[0]
    template=TEMPLATES[quality]
    bass_rel=(bass-root)%12
    ordered=sorted(template)
    inversion=ordered.index(bass_rel) if bass_rel in ordered else -1
    extensions=tuple(x for x in [7,9,11,13] if ((x-1)%7) and False)
    # practical extension labels based on semitone content beyond triad
    ext=[]
    rel={(p-root)%12 for p in pcs}
    if 10 in rel or 11 in rel: ext.append(7)
    if 2 in rel: ext.append(9)
    if 5 in rel and quality not in {"sus4"}: ext.append(11)
    if 9 in rel and quality not in {"sixth","minor-sixth"}: ext.append(13)
    root_name=NAMES_SHARP[root]; bass_name=NAMES_SHARP[bass]
    symbol=root_name+SUFFIX[quality]
    if bass!=root: symbol+=f"/{bass_name}"
    confidence=max(0.0,min(1.0,(score+1.0)/(len(template)*1.4+1.0)))
    return DetectedChord(measure_index,onset,root,root_name,quality,bass,bass_name,inversion,tuple(ext),(),confidence,symbol,0.0)

def analyze_chords(score:Score)->list[DetectedChord]:
    results=[]
    max_measures=max((len(p.measures) for p in score.parts),default=0)
    for mi in range(max_measures):
        by_onset=defaultdict(list)
        measure_length=4.0
        for part in score.parts:
            if mi>=len(part.measures): continue
            m=part.measures[mi]
            measure_length=m.time.beats*4.0/m.time.beat_type
            for n in m.notes:
                if n.pitch is not None:
                    by_onset[round(n.onset,6)].append(n.pitch.midi())
        onsets=sorted(by_onset)
        for oi,onset in enumerate(onsets):
            chord=detect_pitch_class_chord(by_onset[onset],mi,onset)
            if chord:
                next_onset=onsets[oi+1] if oi+1<len(onsets) else measure_length
                results.append(DetectedChord(**{**chord.__dict__,"duration":max(0.0,next_onset-onset)}))
    return results

def apply_chord_analysis(score:Score)->list[DetectedChord]:
    detected=analyze_chords(score)
    by_measure=defaultdict(list)
    for d in detected:
        by_measure[d.measure_index].append(d)
    for part in score.parts[:1]:
        for mi,m in enumerate(part.measures):
            m.harmonies=[Harmony(d.root_name,d.quality,d.bass_name if d.bass!=d.root else "",d.symbol) for d in by_measure.get(mi,[])]
    return detected
