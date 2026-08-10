from __future__ import annotations
from dataclasses import dataclass,field
from harmonia_studio.score import Score
from harmonia_studio.harmony.voice_leading import validate_voice_leading
from harmonia_studio.analysis.chords import analyze_chords
from harmonia_studio.analysis.phrases import analyze_phrases

@dataclass
class QualityMetrics:
    melody_preservation:float
    voice_leading:float
    range_compliance:float
    harmonic_consistency:float
    cadence_quality:float
    style_consistency:float
    playability:float
    rhythmic_consistency:float

    @property
    def overall(self)->float:
        vals=[
            self.melody_preservation,self.voice_leading,self.range_compliance,
            self.harmonic_consistency,self.cadence_quality,self.style_consistency,
            self.playability,self.rhythmic_consistency,
        ]
        return sum(vals)/len(vals)

@dataclass
class QualityReport:
    metrics:QualityMetrics
    warnings:list[str]=field(default_factory=list)
    issue_counts:dict[str,int]=field(default_factory=dict)

def _melody_signature(score:Score):
    if not score.parts: return []
    out=[]
    for mi,m in enumerate(score.parts[0].measures):
        for n in m.notes:
            if n.pitch is not None:
                out.append((mi,round(n.onset,4),n.pitch.midi(),round(n.duration,4)))
    return out

def _melody_score(reference:Score|None,arranged:Score)->float:
    if reference is None: return 100.0
    a=_melody_signature(reference); b=_melody_signature(arranged)
    if not a and not b: return 100.0
    if not a: return 0.0
    matches=sum(1 for x,y in zip(a,b) if x==y)
    return 100.0*matches/max(len(a),len(b),1)

def _rhythm_score(score:Score)->float:
    total=0; bad=0
    for part in score.parts:
        for m in part.measures:
            length=m.time.beats*4.0/m.time.beat_type
            for n in m.notes:
                total+=1
                if n.onset<0 or n.duration<=0 or n.onset+n.duration>length+1e-6:
                    bad+=1
    return 100.0 if total==0 else max(0.0,100.0-100.0*bad/total)

def analyze_quality(arranged:Score,reference_melody:Score|None=None,expected_style:str|None=None)->QualityReport:
    issues=validate_voice_leading(arranged)
    counts={}
    for i in issues: counts[i.code]=counts.get(i.code,0)+1
    errors=sum(1 for i in issues if i.severity=="error")
    warnings_count=sum(1 for i in issues if i.severity!="error")
    voice=max(0.0,100.0-errors*8-warnings_count*2)
    range_count=counts.get("range",0)
    range_score=max(0.0,100.0-range_count*15)
    playability=max(0.0,100.0-(range_count+counts.get("excessive-leap",0)+counts.get("voice-crossing",0))*8)

    chords=analyze_chords(arranged)
    harmonic=100.0 if not chords else 100.0*sum(c.confidence for c in chords)/len(chords)
    phrases=analyze_phrases(arranged)
    cadence=70.0 if not phrases.cadences else min(100.0,100.0*sum(c.confidence for c in phrases.cadences)/len(phrases.cadences))
    style_actual=arranged.metadata.get("harmonyStyle") or arranged.metadata.get("arrangementStyle")
    if expected_style is None:
        style_score=100.0 if style_actual else 80.0
    else:
        style_score=100.0 if style_actual==expected_style else 45.0
    rhythm=_rhythm_score(arranged)
    metrics=QualityMetrics(
        _melody_score(reference_melody,arranged),voice,range_score,harmonic,cadence,style_score,playability,rhythm
    )
    messages=[f"{i.code}: {i.message} (measure {i.measure_index+1})" for i in issues]
    return QualityReport(metrics,messages,counts)
