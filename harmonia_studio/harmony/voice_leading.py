from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from harmonia_studio.score import Score
from harmonia_studio.analysis.tonal import analyze_tonality, NAMES

DEFAULT_RANGES={
    "soprano":(60,81),
    "alto":(53,74),
    "tenor":(48,69),
    "bass":(36,60),
}

@dataclass(frozen=True)
class VoiceLeadingIssue:
    code:str
    severity:str
    message:str
    measure_index:int
    onset:float
    voices:tuple[int,...]=()

@dataclass
class VoiceLeadingProfile:
    ranges:dict[str,tuple[int,int]]=field(default_factory=lambda:dict(DEFAULT_RANGES))
    max_leap:int=12
    max_upper_spacing:int=12
    forbid_parallel_fifths:bool=True
    forbid_parallel_octaves:bool=True
    check_hidden_perfects:bool=True
    resolve_leading_tone:bool=True

def _events_for_part(part):
    out={}
    for mi,m in enumerate(part.measures):
        for n in m.notes:
            if n.pitch is not None:
                out[(mi,round(n.onset,4))]=n.pitch.midi()
    return out

def validate_voice_leading(score:Score,profile:VoiceLeadingProfile|None=None)->list[VoiceLeadingIssue]:
    p=profile or VoiceLeadingProfile()
    issues=[]
    parts=score.parts[:4]
    events=[_events_for_part(part) for part in parts]
    role_names=["soprano","alto","tenor","bass"]

    # Range and melodic leap checks
    for vi,e in enumerate(events):
        role=role_names[vi] if vi<4 else f"voice{vi}"
        lo,hi=p.ranges.get(role,(0,127))
        seq=sorted(e.items())
        for (mi,on),pitch in seq:
            if pitch<lo or pitch>hi:
                issues.append(VoiceLeadingIssue("range","error",f"{role.title()} pitch {pitch} outside {lo}-{hi}",mi,on,(vi,)))
        for ((mi1,on1),a),((mi2,on2),b) in zip(seq,seq[1:]):
            if abs(b-a)>p.max_leap:
                issues.append(VoiceLeadingIssue("excessive-leap","warning",f"{role.title()} leap of {abs(b-a)} semitones",mi2,on2,(vi,)))

    keys=sorted(set().union(*(set(e.keys()) for e in events)))
    previous=None
    for key in keys:
        pitches=[e.get(key) for e in events]
        mi,on=key
        # Crossing/spacing only when adjacent voices present
        for vi in range(len(pitches)-1):
            a,b=pitches[vi],pitches[vi+1]
            if a is not None and b is not None:
                if a < b:
                    issues.append(VoiceLeadingIssue("voice-crossing","error","Upper voice lies below lower voice",mi,on,(vi,vi+1)))
                if vi<2 and a-b>p.max_upper_spacing:
                    issues.append(VoiceLeadingIssue("spacing","warning","Upper voices exceed allowed spacing",mi,on,(vi,vi+1)))

        if previous:
            prev_key,prev_pitches=previous
            for i in range(len(pitches)):
                for j in range(i+1,len(pitches)):
                    a1,b1=prev_pitches[i],prev_pitches[j]
                    a2,b2=pitches[i],pitches[j]
                    if None in (a1,b1,a2,b2): continue
                    int1=abs(a1-b1)%12; int2=abs(a2-b2)%12
                    dir_a=(a2>a1)-(a2<a1); dir_b=(b2>b1)-(b2<b1)
                    similar=dir_a==dir_b and dir_a!=0
                    if similar and int1==7 and int2==7 and p.forbid_parallel_fifths:
                        issues.append(VoiceLeadingIssue("parallel-fifth","error","Parallel perfect fifth",mi,on,(i,j)))
                    if similar and int1==0 and int2==0 and p.forbid_parallel_octaves:
                        issues.append(VoiceLeadingIssue("parallel-octave","error","Parallel octave/unison",mi,on,(i,j)))
                    if p.check_hidden_perfects and i==0 and j==len(pitches)-1 and similar and int2 in {0,7} and int1 not in {0,7}:
                        issues.append(VoiceLeadingIssue("hidden-perfect","warning","Direct/hidden perfect interval in outer voices",mi,on,(i,j)))
            # Leading tone resolution for soprano
            if p.resolve_leading_tone and prev_pitches and pitches and prev_pitches[0] is not None and pitches[0] is not None:
                tonal=analyze_tonality(score).global_key
                tonic=NAMES.index(tonal.tonic)
                leading=(tonic-1)%12
                if prev_pitches[0]%12==leading and pitches[0]%12!=tonic:
                    issues.append(VoiceLeadingIssue("unresolved-leading-tone","warning","Leading tone does not resolve to tonic",mi,on,(0,)))
        previous=(key,pitches)
    return issues
