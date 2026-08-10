from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from harmonia_studio.importers.audio import AudioData,load_audio

NAMES=["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]
TEMPLATES={
    "major":(0,4,7),
    "minor":(0,3,7),
    "dominant-seventh":(0,4,7,10),
    "minor-seventh":(0,3,7,10),
}
SUFFIX={"major":"","minor":"m","dominant-seventh":"7","minor-seventh":"m7"}

@dataclass
class AudioChordSegment:
    start_seconds:float
    end_seconds:float
    root:int
    root_name:str
    quality:str
    symbol:str
    confidence:float

@dataclass
class ChordRecognitionResult:
    segments:list[AudioChordSegment]
    window_seconds:float

    def correct(self,index:int,root_name:str,quality:str)->None:
        if root_name not in NAMES: raise ValueError("Unknown root")
        if quality not in TEMPLATES: raise ValueError("Unknown quality")
        s=self.segments[index]
        s.root=NAMES.index(root_name); s.root_name=root_name; s.quality=quality
        s.symbol=root_name+SUFFIX[quality]; s.confidence=1.0

def _template_vector(root:int,quality:str)->np.ndarray:
    v=np.zeros(12,dtype=float)
    ints=TEMPLATES[quality]
    weights=[1.0,.9,.85,.7]
    for i,interval in enumerate(ints):
        v[(root+interval)%12]=weights[min(i,len(weights)-1)]
    return v/np.linalg.norm(v)

_TEMPLATE_CACHE=[(r,q,_template_vector(r,q)) for r in range(12) for q in TEMPLATES]

def recognize_audio_chords(source:str|AudioData,window_seconds:float=1.0)->ChordRecognitionResult:
    import librosa
    audio=load_audio(source) if isinstance(source,(str,bytes)) else source
    y=audio.samples; sr=audio.sample_rate
    if len(y)==0: return ChordRecognitionResult([],window_seconds)
    hop=512
    chroma=librosa.feature.chroma_stft(y=y,sr=sr,n_fft=4096,hop_length=hop)
    frame_times=librosa.frames_to_time(np.arange(chroma.shape[1]),sr=sr,hop_length=hop)
    duration=len(y)/sr
    segments=[]
    start=0.0
    while start<duration:
        end=min(duration,start+window_seconds)
        mask=(frame_times>=start)&(frame_times<end)
        vec=np.mean(chroma[:,mask],axis=1) if np.any(mask) else np.zeros(12)
        norm=np.linalg.norm(vec)
        scores=[]
        if norm>0:
            u=vec/norm
            for root,q,t in _TEMPLATE_CACHE:
                scores.append((float(np.dot(u,t)),root,q))
        if scores:
            scores.sort(reverse=True)
            best=scores[0]; second=scores[1][0] if len(scores)>1 else 0.0
            raw,root,q=best
            conf=max(0.0,min(1.0,(raw-second+.05)/.25))
            segments.append(AudioChordSegment(start,end,root,NAMES[root],q,NAMES[root]+SUFFIX[q],conf))
        start=end
    # Merge adjacent identical chords.
    merged=[]
    for s in segments:
        if merged and merged[-1].root==s.root and merged[-1].quality==s.quality:
            prev=merged[-1]
            prev.end_seconds=s.end_seconds
            prev.confidence=(prev.confidence+s.confidence)/2
        else:
            merged.append(s)
    return ChordRecognitionResult(merged,window_seconds)
