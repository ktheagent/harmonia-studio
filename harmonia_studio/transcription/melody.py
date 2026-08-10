from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch, TimeSignature, KeySignature
from harmonia_studio.importers.audio import AudioData, load_audio

@dataclass(frozen=True)
class TranscribedNote:
    midi:int
    start_seconds:float
    end_seconds:float
    confidence:float

@dataclass
class MelodyTranscription:
    score:Score
    notes:list[TranscribedNote]
    confidence:float

def transcribe_melody(source:str|AudioData,bpm:float=120.0,hop_length:int=256)->MelodyTranscription:
    import librosa
    audio=load_audio(source) if isinstance(source,(str,bytes)) else source
    y=audio.samples; sr=audio.sample_rate
    if len(y)<512:
        return MelodyTranscription(Score("Transcription","",[Part("P1","Melody",Instrument("Voice",52),[])]),[],0.0)
    f0,voiced_flag,voiced_prob=librosa.pyin(
        y,fmin=librosa.note_to_hz("C2"),fmax=librosa.note_to_hz("C7"),
        sr=sr,frame_length=2048,hop_length=hop_length
    )
    frame_times=librosa.frames_to_time(np.arange(len(f0)),sr=sr,hop_length=hop_length)
    midi=np.full(len(f0),-1,dtype=int)
    valid=np.isfinite(f0) & voiced_flag
    midi[valid]=np.rint(librosa.hz_to_midi(f0[valid])).astype(int)
    notes=[]
    start=None; cur=None; probs=[]
    for i,m in enumerate(midi):
        is_voiced=m>=0 and (voiced_prob[i] if np.isfinite(voiced_prob[i]) else 0)>=0.2
        if is_voiced:
            if cur is None:
                cur=int(m); start=i; probs=[float(voiced_prob[i])]
            elif abs(int(m)-cur)<=0:
                probs.append(float(voiced_prob[i]))
            else:
                st=float(frame_times[start]); en=float(frame_times[i])
                if en-st>=0.04:
                    notes.append(TranscribedNote(cur,st,en,float(np.mean(probs))))
                cur=int(m); start=i; probs=[float(voiced_prob[i])]
        elif cur is not None:
            st=float(frame_times[start]); en=float(frame_times[i])
            if en-st>=0.04:
                notes.append(TranscribedNote(cur,st,en,float(np.mean(probs))))
            cur=None; start=None; probs=[]
    if cur is not None:
        st=float(frame_times[start]); en=min(len(y)/sr,float(frame_times[-1]+hop_length/sr))
        if en-st>=0.04: notes.append(TranscribedNote(cur,st,en,float(np.mean(probs))))

    # Merge adjacent same-pitch fragments separated by tiny gaps.
    merged=[]
    for n in notes:
        if merged and merged[-1].midi==n.midi and n.start_seconds-merged[-1].end_seconds<=0.08:
            prev=merged[-1]
            merged[-1]=TranscribedNote(prev.midi,prev.start_seconds,n.end_seconds,(prev.confidence+n.confidence)/2)
        else:
            merged.append(n)
    notes=merged
    qps=max(1.0,bpm)/60.0
    measure_len=4.0
    count=max(1,int(math.ceil(max((n.end_seconds*qps for n in notes),default=4)/measure_len)))
    measures=[Measure(i+1,time=TimeSignature(4,4),key=KeySignature(),tempo=bpm) for i in range(count)]
    for n in notes:
        onset_q=n.start_seconds*qps
        mi=min(count-1,int(onset_q//measure_len))
        local=onset_q-mi*measure_len
        dur=max(0.125,(n.end_seconds-n.start_seconds)*qps)
        measures[mi].notes.append(Note(Pitch.from_midi(n.midi),dur,onset=local))
    score=Score("Audio Transcription","",[Part("P1","Melody",Instrument("Voice",52),measures)],{"sourceFormat":"Audio","transcription":"predominant-melody"})
    confidence=float(np.mean([n.confidence for n in notes])) if notes else 0.0
    return MelodyTranscription(score,notes,confidence)
