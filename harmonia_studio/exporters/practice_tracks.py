from __future__ import annotations
from pathlib import Path
import re
from harmonia_studio.score import Score
from .audio import export_audio

VOICE_NAMES={"soprano","alto","tenor","bass","voice","vocal","lead vocal"}

def _slug(text:str)->str:
    s=re.sub(r"[^a-zA-Z0-9]+","-",text.strip()).strip("-").lower()
    return s or "part"

def export_practice_tracks(score:Score,output_dir:str|Path,format:str="wav",sample_rate:int=44100)->dict[str,Path]:
    ext=format.lower().lstrip(".")
    if ext not in {"wav","mp3"}: raise ValueError("Practice tracks support WAV or MP3")
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    files={}
    files["full_mix"]=export_audio(score,out/f"full-mix.{ext}",sample_rate)
    for pi,part in enumerate(score.parts):
        volumes={i:(1.35 if i==pi else .28) for i in range(len(score.parts))}
        key=f"{_slug(part.name)}_emphasized"
        files[key]=export_audio(score,out/f"{_slug(part.name)}-emphasized.{ext}",sample_rate,volumes)
    voice_indices=[]
    for i,p in enumerate(score.parts):
        name=p.name.strip().lower(); inst=p.instrument.name.strip().lower()
        if name in VOICE_NAMES or inst in {"voice","vocal"}:
            voice_indices.append(i)
    volumes={i:(0.0 if i in voice_indices else 1.0) for i in range(len(score.parts))}
    files["instrument_only"]=export_audio(score,out/f"instrument-only.{ext}",sample_rate,volumes)
    return files
