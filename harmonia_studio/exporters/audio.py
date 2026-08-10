from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import math, shutil, subprocess
import numpy as np
from harmonia_studio.score import Score

def midi_frequency(midi:int)->float:
    return 440.0*(2.0**((midi-69)/12.0))

def render_score_audio(score:Score,sample_rate:int=44100,part_volumes:dict[int,float]|None=None)->np.ndarray:
    part_volumes=part_volumes or {}
    scheduled=[]
    total=0.25
    for pi,part in enumerate(score.parts):
        abs_sec=0.0
        for m in part.measures:
            sec_per_q=60.0/max(1.0,m.tempo)
            for n in m.notes:
                if n.pitch is None: continue
                start=abs_sec+n.onset*sec_per_q
                dur=max(.02,n.duration*sec_per_q)
                scheduled.append((start,dur,n.pitch.midi(),n.velocity,pi))
                total=max(total,start+dur+.1)
            abs_sec += (m.time.beats*4.0/m.time.beat_type)*sec_per_q
            total=max(total,abs_sec)
    y=np.zeros(int(math.ceil(total*sample_rate)),dtype=np.float32)
    for start,dur,midi,velocity,pi in scheduled:
        a=int(start*sample_rate); count=max(1,int(dur*sample_rate)); b=min(len(y),a+count)
        if b<=a: continue
        t=np.arange(b-a,dtype=np.float32)/sample_rate
        f=midi_frequency(midi)
        tone=np.sin(2*np.pi*f*t)+0.18*np.sin(2*np.pi*2*f*t)
        env=np.ones_like(tone)
        attack=min(len(env),max(1,int(.01*sample_rate)))
        release=min(len(env),max(1,int(.05*sample_rate)))
        env[:attack]*=np.linspace(0,1,attack,endpoint=True)
        env[-release:]*=np.linspace(1,0,release,endpoint=True)
        volume=max(0.0,min(2.0,float(part_volumes.get(pi,1.0))))
        amp=.12*(velocity/127.0)*volume
        y[a:b]+=tone.astype(np.float32)*env*amp
    peak=float(np.max(np.abs(y))) if len(y) else 0
    if peak>.98: y*=.98/peak
    return y

def export_audio(score:Score,path:str|Path,sample_rate:int=44100,part_volumes:dict[int,float]|None=None)->Path:
    import soundfile as sf
    p=Path(path); ext=p.suffix.lower()
    if ext not in {".wav",".mp3"}:
        raise ValueError("Audio export supports WAV and MP3")
    p.parent.mkdir(parents=True,exist_ok=True)
    y=render_score_audio(score,sample_rate,part_volumes)
    if ext==".wav":
        sf.write(str(p),y,sample_rate,subtype="PCM_16")
        return p
    exe=shutil.which("ffmpeg")
    if not exe: raise RuntimeError("ffmpeg is required for MP3 export")
    with TemporaryDirectory(prefix="harmonia-audio-") as td:
        wav=Path(td)/"mix.wav"; sf.write(str(wav),y,sample_rate,subtype="PCM_16")
        proc=subprocess.run([exe,"-y","-hide_banner","-loglevel","error","-i",str(wav),"-codec:a","libmp3lame","-q:a","2",str(p)],capture_output=True,text=True,timeout=120)
        if proc.returncode!=0: raise RuntimeError(proc.stderr.strip() or "MP3 export failed")
    return p
