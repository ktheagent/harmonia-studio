from __future__ import annotations
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from harmonia_studio.score import Score

def _sub(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag, attrs)
    if text is not None:
        e.text = str(text)
    return e

def _duration_type(q: float) -> str:
    choices = [(4, "whole"), (2, "half"), (1, "quarter"), (.5, "eighth"), (.25, "16th"), (.125, "32nd")]
    return min(choices, key=lambda x: abs(q-x[0]))[1]

def _ticks(value: float, divisions: int) -> int:
    return max(0, int(round(value * divisions)))

def _emit_note(parent, note, divisions: int, *, chord: bool = False) -> None:
    ne = _sub(parent, "note")
    if chord:
        _sub(ne, "chord")
    if note.is_rest:
        _sub(ne, "rest")
    else:
        pit = _sub(ne, "pitch")
        _sub(pit, "step", note.pitch.step)
        if note.pitch.alter:
            _sub(pit, "alter", note.pitch.alter)
        _sub(pit, "octave", note.pitch.octave)
    _sub(ne, "duration", max(1, _ticks(note.duration, divisions)))
    _sub(ne, "voice", note.voice)
    _sub(ne, "type", _duration_type(note.duration))
    for _ in range(note.dots):
        _sub(ne, "dot")
    if note.tie_start:
        _sub(ne, "tie", type="start")
    if note.tie_stop:
        _sub(ne, "tie", type="stop")
    _sub(ne, "staff", note.staff)
    for lyr in note.lyrics:
        le = _sub(ne, "lyric")
        if lyr.syllabic:
            _sub(le, "syllabic", lyr.syllabic)
        _sub(le, "text", lyr.text)

def _emit_timed_notes(measure_el, notes, divisions: int) -> None:
    by_voice = {}
    for index, note in enumerate(notes):
        by_voice.setdefault(note.voice, []).append((index, note))

    previous_cursor = 0
    first_voice = True
    for voice in sorted(by_voice):
        if not first_voice and previous_cursor > 0:
            backup = _sub(measure_el, "backup")
            _sub(backup, "duration", previous_cursor)
        first_voice = False

        cursor = 0
        last_onset = None
        voice_notes = sorted(
            by_voice[voice],
            key=lambda item: (item[1].onset, item[0]),
        )
        for _, note in voice_notes:
            target = _ticks(note.onset, divisions)
            chord = last_onset is not None and target == last_onset
            if not chord:
                if target > cursor:
                    forward = _sub(measure_el, "forward")
                    _sub(forward, "duration", target - cursor)
                    cursor = target
                elif target < cursor:
                    backup = _sub(measure_el, "backup")
                    _sub(backup, "duration", cursor - target)
                    cursor = target
            _emit_note(measure_el, note, divisions, chord=chord)
            if not chord:
                cursor = target + max(1, _ticks(note.duration, divisions))
                last_onset = target
        previous_cursor = cursor

def export_musicxml(score: Score, path: str | Path, divisions: int = 480) -> Path:
    p = Path(path)
    root = ET.Element("score-partwise", {"version": "4.0"})
    work = _sub(root, "work")
    _sub(work, "work-title", score.title)
    identification = _sub(root, "identification")
    if score.composer:
        _sub(identification, "creator", score.composer, type="composer")
    part_list = _sub(root, "part-list")
    for part in score.parts:
        sp = _sub(part_list, "score-part", id=part.id)
        _sub(sp, "part-name", part.name)
    for part in score.parts:
        pe = _sub(root, "part", id=part.id)
        for mi, m in enumerate(part.measures):
            me = _sub(pe, "measure", number=str(m.number))
            attrs = _sub(me, "attributes")
            _sub(attrs, "divisions", divisions)
            key = _sub(attrs, "key")
            _sub(key, "fifths", m.key.fifths)
            _sub(key, "mode", m.key.mode)
            te = _sub(attrs, "time")
            _sub(te, "beats", m.time.beats)
            _sub(te, "beat-type", m.time.beat_type)
            if mi == 0:
                clef = _sub(attrs, "clef")
                _sub(clef, "sign", "G")
                _sub(clef, "line", "2")
                direction = _sub(me, "direction", placement="above")
                dt = _sub(direction, "direction-type")
                met = _sub(dt, "metronome")
                _sub(met, "beat-unit", "quarter")
                _sub(met, "per-minute", f"{m.tempo:g}")
                _sub(direction, "sound", tempo=f"{m.tempo:g}")
            for h in m.harmonies:
                he = _sub(me, "harmony")
                re = _sub(he, "root")
                root_step = h.root[0] if h.root else "C"
                _sub(re, "root-step", root_step)
                if len(h.root) > 1:
                    alter = 1 if "#" in h.root else -1 if "b" in h.root else 0
                    if alter:
                        _sub(re, "root-alter", alter)
                kind = _sub(he, "kind", h.kind)
                if h.symbol:
                    kind.set("text", h.symbol)
                if h.bass:
                    be = _sub(he, "bass")
                    _sub(be, "bass-step", h.bass[0])
                    if len(h.bass) > 1:
                        alter = 1 if "#" in h.bass else -1 if "b" in h.bass else 0
                        if alter:
                            _sub(be, "bass-alter", alter)
            _emit_timed_notes(me, m.notes, divisions)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if p.suffix.lower() == ".mxl":
        p.parent.mkdir(parents=True, exist_ok=True)
        container = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<container><rootfiles><rootfile full-path="score.musicxml" '
            'media-type="application/vnd.recordare.musicxml+xml"/></rootfiles></container>'
        )
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("META-INF/container.xml", container)
            z.writestr("score.musicxml", xml_bytes)
    else:
        if p.suffix.lower() not in {".musicxml", ".xml"}:
            p = p.with_suffix(".musicxml")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(xml_bytes)
    return p
