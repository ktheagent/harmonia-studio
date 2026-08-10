from __future__ import annotations
from dataclasses import dataclass,field
import re
from harmonia_studio.score import Score,Pitch
from harmonia_studio.harmony.styles import harmonize_style,STYLE_REGISTRY
from harmonia_studio.harmony.region import reharmonize_region
from harmonia_studio.harmony.candidates import generate_candidates,HarmonyCandidate
from harmonia_studio.arrangement.engine import auto_arrange
from harmonia_studio.quality import analyze_quality,QualityReport

STYLE_ALIASES={
    "gospel":"gospel","jazz":"jazz","hymn":"hymn","classical":"classical",
    "chorale":"classical","pop":"pop","r&b":"rnb","rnb":"rnb","neo-soul":"rnb",
    "neo soul":"rnb","highlife":"highlife","afrobeat":"afrobeat","blues":"blues",
}
ENSEMBLES={
    "satb":"satb","choir":"satb","piano accompaniment":"piano_vocal",
    "piano and vocal":"piano_vocal","string quartet":"string_quartet",
    "jazz combo":"jazz_combo","worship band":"worship_band","orchestra":"orchestra",
}

@dataclass
class MusicCommand:
    raw_text:str
    action:str="harmonize"
    style:str="hymn"
    complexity:str="balanced"
    measure_range:tuple[int,int]|None=None  # zero based inclusive
    preserve_melody:bool=True
    ensemble:str|None=None
    candidate_count:int=1
    easier_voices:list[str]=field(default_factory=list)
    bass_movement:str|None=None
    ending_style:str|None=None

@dataclass
class AssistantResult:
    command:MusicCommand
    score:Score
    quality:QualityReport
    candidates:list[HarmonyCandidate]=field(default_factory=list)

def parse_music_command(text:str)->MusicCommand:
    lower=text.lower()
    cmd=MusicCommand(text)
    for alias,style in sorted(STYLE_ALIASES.items(),key=lambda x:-len(x[0])):
        if alias in lower:
            cmd.style=style; break
    if any(x in lower for x in ["advanced","rich","creative"]): cmd.complexity="creative"
    elif any(x in lower for x in ["simple","conservative"]): cmd.complexity="conservative"
    elif any(x in lower for x in ["modern","stylistic"]): cmd.complexity="stylistic"

    m=re.search(r"(?:measures?|bars?)\s+(\d+)\s*(?:-|–|—|to)\s*(\d+)",lower)
    if m:
        a,b=int(m.group(1)),int(m.group(2))
        if a>b: a,b=b,a
        cmd.measure_range=(max(0,a-1),max(0,b-1))
    if any(x in lower for x in ["keep the soprano","keep soprano","preserve melody","keep the melody"]):
        cmd.preserve_melody=True
    for voice in ["soprano","alto","tenor","bass"]:
        if re.search(rf"(?:make\s+)?(?:the\s+)?{voice}\s+(?:part\s+)?(?:easier|simpler)",lower):
            cmd.easier_voices.append(voice)
    if "bass more movement" in lower or "more bass movement" in lower:
        cmd.bass_movement="active"
    em=re.search(r"(?:final|ending|last)\s+(?:cadence\s+)?(?:to|in|as)?\s*(?:a\s+)?(jazz|gospel|classical|blues)",lower)
    if em: cmd.ending_style=STYLE_ALIASES.get(em.group(1),em.group(1))
    for phrase,ensemble in ENSEMBLES.items():
        if phrase in lower:
            cmd.ensemble=ensemble; cmd.action="arrange"; break
    mcount=re.search(r"(?:create|give|generate)?\s*(three|3)\s+(?:alternatives|options|versions|candidates)",lower)
    if mcount:
        cmd.candidate_count=3
    if cmd.measure_range:
        cmd.action="reharmonize-region"
    if "reharmonize" in lower:
        cmd.action="reharmonize-region" if cmd.measure_range else "harmonize"
    return cmd

def _simplify_voice(score:Score,voice_name:str,max_leap:int=7)->None:
    idx={"soprano":0,"alto":1,"tenor":2,"bass":3}.get(voice_name)
    if idx is None or idx>=len(score.parts): return
    prev=None
    ranges={"soprano":(60,81),"alto":(53,74),"tenor":(48,69),"bass":(36,60)}
    lo,hi=ranges[voice_name]
    for m in score.parts[idx].measures:
        for n in m.notes:
            if n.pitch is None: continue
            cur=n.pitch.midi()
            if prev is not None and abs(cur-prev)>max_leap:
                options=[cur+12*k for k in range(-3,4) if lo<=cur+12*k<=hi]
                if options:
                    cur=min(options,key=lambda x:abs(x-prev)); n.pitch=Pitch.from_midi(cur)
            prev=cur

def execute_music_command(score:Score,command:MusicCommand|str)->AssistantResult:
    cmd=parse_music_command(command) if isinstance(command,str) else command
    candidates=[]
    if cmd.candidate_count>=3:
        candidates=generate_candidates(score,cmd.style)
        out=candidates[0].result.score
    elif cmd.action=="reharmonize-region" and cmd.measure_range:
        out=reharmonize_region(score,cmd.measure_range[0],cmd.measure_range[1],cmd.style,cmd.complexity)
    elif cmd.action=="arrange" and cmd.ensemble:
        out=auto_arrange(score,cmd.ensemble,cmd.style,cmd.complexity)
    else:
        out=harmonize_style(score,cmd.style,cmd.complexity).score

    for voice in cmd.easier_voices:
        _simplify_voice(out,voice)
    if cmd.bass_movement:
        out.metadata["requestedBassMovement"]=cmd.bass_movement
    if cmd.ending_style:
        out.metadata["requestedEndingStyle"]=cmd.ending_style
    out.metadata["assistantCommand"]=cmd.raw_text
    quality=analyze_quality(out,score,cmd.style)
    return AssistantResult(cmd,out,quality,candidates)
