from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, shutil, subprocess
import numpy as np

SUPPORTED_AUDIO={".wav",".mp3",".flac",".aac",".m4a"}

@dataclass
class AudioInfo:
    path:Path
    sample_rate:int
    channels:int
    duration:float
    format:str

@dataclass
class AudioData:
    info:AudioInfo
    samples:np.ndarray  # mono float32
    sample_rate:int

def probe_audio(path:str|Path)->AudioInfo:
    p=Path(path)
    if p.suffix.lower() not in SUPPORTED_AUDIO:
        raise ValueError(f"Unsupported audio format: {p.suffix}")
    if not p.is_file():
        raise FileNotFoundError(p)
    try:
        import soundfile as sf
        i=sf.info(str(p))
        return AudioInfo(p,int(i.samplerate),int(i.channels),float(i.duration),p.suffix.lower().lstrip("."))
    except Exception:
        exe=shutil.which("ffprobe")
        if not exe:
            raise RuntimeError("Unable to read audio metadata; ffprobe is not installed")
        cmd=[exe,"-v","error","-select_streams","a:0","-show_entries",
             "stream=sample_rate,channels:format=duration","-of","json",str(p)]
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        if proc.returncode!=0:
            raise RuntimeError(proc.stderr.strip() or "ffprobe failed")
        data=json.loads(proc.stdout)
        stream=data.get("streams",[{}])[0]
        return AudioInfo(p,int(stream.get("sample_rate") or 0),int(stream.get("channels") or 0),
                         float(data.get("format",{}).get("duration") or 0),p.suffix.lower().lstrip("."))

def load_audio(path:str|Path,target_sr:int|None=22050)->AudioData:
    info=probe_audio(path)
    try:
        import librosa
        y,sr=librosa.load(str(info.path),sr=target_sr,mono=True)
    except Exception as e:
        raise RuntimeError(f"Unable to decode audio: {e}") from e
    y=np.asarray(y,dtype=np.float32)
    return AudioData(info,y,int(sr))
