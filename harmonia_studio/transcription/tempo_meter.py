from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from harmonia_studio.importers.audio import AudioData,load_audio

@dataclass
class TempoMeterAnalysis:
    bpm:float
    beat_times:list[float]
    meter_numerator:int
    meter_denominator:int
    meter_confidence:float
    pickup_beats:int
    tempo_confidence:float

def detect_tempo_meter(source:str|AudioData)->TempoMeterAnalysis:
    import librosa
    audio=load_audio(source) if isinstance(source,(str,bytes)) else source
    y=audio.samples; sr=audio.sample_rate
    if len(y)<1024:
        return TempoMeterAnalysis(0.0,[],4,4,0.0,0,0.0)
    hop=512
    onset=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
    tempo,beats=librosa.beat.beat_track(onset_envelope=onset,sr=sr,hop_length=hop,units="frames")
    bpm=float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
    beats=np.asarray(beats,dtype=int)
    beat_times=librosa.frames_to_time(beats,sr=sr,hop_length=hop).tolist()
    strengths=onset[beats] if len(beats) else np.array([])
    # Meter hypothesis: the downbeat phase should carry greater average onset energy.
    hypotheses=[]
    for meter in (3,4,6):
        if len(strengths)<meter*2: continue
        for phase in range(meter):
            down=strengths[phase::meter]
            others=np.array([v for i,v in enumerate(strengths) if i%meter!=phase],dtype=float)
            if len(down)==0 or len(others)==0: continue
            score=(float(np.mean(down))+1e-6)/(float(np.mean(others))+1e-6)
            stability=1.0/(1.0+float(np.std(down))/(float(np.mean(down))+1e-6))
            hypotheses.append((score*stability,meter,phase))
    if hypotheses:
        hypotheses.sort(reverse=True)
        best_score,meter,phase=hypotheses[0]
        second=hypotheses[1][0] if len(hypotheses)>1 else 1.0
        meter_conf=max(0.0,min(1.0,(best_score-second+.1)/.7))
    else:
        meter,phase,meter_conf=4,0,0.0
    # Simple regularity confidence for tempo.
    if len(beat_times)>=3:
        intervals=np.diff(beat_times)
        cv=float(np.std(intervals)/(np.mean(intervals)+1e-9))
        tempo_conf=max(0.0,min(1.0,1.0-cv*4))
    else:
        tempo_conf=0.0
    pickup_beats=int(phase) if phase else 0
    return TempoMeterAnalysis(bpm,[float(x) for x in beat_times],int(meter),4,float(meter_conf),pickup_beats,float(tempo_conf))
