from __future__ import annotations
from pathlib import Path
from harmonia_studio.score import Score

def export_midi(score:Score,path:str|Path,ticks_per_beat:int=480)->Path:
    try:
        import mido
    except ImportError as e:
        raise RuntimeError("mido is required for MIDI export") from e
    p=Path(path)
    if p.suffix.lower() not in {".mid",".midi"}: p=p.with_suffix(".mid")
    p.parent.mkdir(parents=True,exist_ok=True)
    mid=mido.MidiFile(type=1,ticks_per_beat=ticks_per_beat)

    meta=mido.MidiTrack(); mid.tracks.append(meta)
    meta.append(mido.MetaMessage("track_name",name=score.title or "Harmonia Studio",time=0))
    # Global timeline from first part.
    if score.parts:
        events=[]; abs_q=0.0; last_tempo=None; last_ts=None
        for m in score.parts[0].measures:
            tick=int(round(abs_q*ticks_per_beat))
            if m.tempo!=last_tempo:
                events.append((tick,0,mido.MetaMessage("set_tempo",tempo=mido.bpm2tempo(max(1,m.tempo)),time=0)))
                last_tempo=m.tempo
            ts=(m.time.beats,m.time.beat_type)
            if ts!=last_ts:
                events.append((tick,1,mido.MetaMessage("time_signature",numerator=m.time.beats,denominator=m.time.beat_type,time=0)))
                last_ts=ts
            abs_q += m.time.beats*4.0/m.time.beat_type
        prev=0
        for tick,_,msg in sorted(events,key=lambda x:(x[0],x[1])):
            msg.time=max(0,tick-prev); meta.append(msg); prev=tick
    meta.append(mido.MetaMessage("end_of_track",time=0))

    for pi,part in enumerate(score.parts):
        track=mido.MidiTrack(); mid.tracks.append(track)
        track.append(mido.MetaMessage("track_name",name=part.name,time=0))
        channel=pi%16
        if channel==9: channel=10 if pi%16!=10 else 11
        track.append(mido.Message("program_change",program=max(0,min(127,part.instrument.midi_program)),channel=channel,time=0))
        events=[]; abs_q=0.0
        for m in part.measures:
            for n in m.notes:
                if n.pitch is None: continue
                start=int(round((abs_q+n.onset)*ticks_per_beat))
                end=int(round((abs_q+n.onset+n.duration)*ticks_per_beat))
                pitch=max(0,min(127,n.pitch.midi())); vel=max(1,min(127,n.velocity))
                events.append((start,1,mido.Message("note_on",note=pitch,velocity=vel,channel=channel,time=0)))
                events.append((max(start+1,end),0,mido.Message("note_off",note=pitch,velocity=0,channel=channel,time=0)))
            abs_q += m.time.beats*4.0/m.time.beat_type
        prev=0
        for tick,_,msg in sorted(events,key=lambda x:(x[0],x[1])):
            msg.time=max(0,tick-prev); track.append(msg); prev=tick
        track.append(mido.MetaMessage("end_of_track",time=0))
    mid.save(str(p))
    return p
