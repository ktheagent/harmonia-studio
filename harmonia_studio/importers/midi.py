from __future__ import annotations
from pathlib import Path
import math
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch, TimeSignature, KeySignature

def _quantize(value: float, grid: float) -> float:
    if grid <= 0:
        return value
    return round(value / grid) * grid

def import_midi(path: str | Path, quantization: float = 0.25) -> Score:
    try:
        import pretty_midi
    except ImportError as e:
        raise RuntimeError("pretty_midi is required for MIDI import") from e
    p = Path(path)
    pm = pretty_midi.PrettyMIDI(str(p))
    tempo_times, tempi = pm.get_tempo_changes()
    tempo = float(tempi[0]) if len(tempi) else 120.0
    ts_changes = pm.time_signature_changes
    if ts_changes:
        ts0 = ts_changes[0]
        time_sig = TimeSignature(ts0.numerator, ts0.denominator)
    else:
        time_sig = TimeSignature(4, 4)
    measure_quarters = time_sig.beats * (4.0 / time_sig.beat_type)
    resolution = float(pm.resolution)
    parts = []
    for idx, inst in enumerate(pm.instruments, start=1):
        name = inst.name or ("Drums" if inst.is_drum else f"Track {idx}")
        midi_program = int(inst.program)
        events = []
        for n in inst.notes:
            start_q = _quantize(pm.time_to_tick(n.start) / resolution, quantization)
            end_q = _quantize(pm.time_to_tick(n.end) / resolution, quantization)
            duration = max(quantization or 0.01, end_q - start_q)
            events.append((start_q, duration, n.pitch, n.velocity))
        max_end = max((s + d for s, d, _, _ in events), default=measure_quarters)
        count = max(1, int(math.ceil(max_end / measure_quarters)))
        measures = [
            Measure(i + 1, time=TimeSignature(time_sig.beats, time_sig.beat_type),
                    key=KeySignature(), tempo=tempo)
            for i in range(count)
        ]
        for start_q, duration, pitch_num, velocity in events:
            mi = min(count - 1, int(start_q // measure_quarters))
            local_onset = start_q - mi * measure_quarters
            measures[mi].notes.append(
                Note(Pitch.from_midi(int(pitch_num)), duration, velocity=int(velocity), onset=local_onset)
            )
        for m in measures:
            m.notes.sort(key=lambda n: (n.onset, n.pitch.midi() if n.pitch else -1))
        parts.append(Part(f"P{idx}", name, Instrument(name, midi_program), measures))
    return Score(p.stem, "", parts, {"sourceFormat": "MIDI", "sourcePath": str(p), "resolution": pm.resolution})
