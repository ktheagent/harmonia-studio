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

            for n in m.notes:
                ne = _sub(me, "note")
                if n.is_rest:
                    _sub(ne, "rest")
                else:
                    pit = _sub(ne, "pitch")
                    _sub(pit, "step", n.pitch.step)
                    if n.pitch.alter:
                        _sub(pit, "alter", n.pitch.alter)
                    _sub(pit, "octave", n.pitch.octave)
                _sub(ne, "duration", max(1, int(round(n.duration * divisions))))
                _sub(ne, "voice", n.voice)
                _sub(ne, "type", _duration_type(n.duration))
                for _ in range(n.dots):
                    _sub(ne, "dot")
                if n.tie_start:
                    _sub(ne, "tie", type="start")
                if n.tie_stop:
                    _sub(ne, "tie", type="stop")
                _sub(ne, "staff", n.staff)
                for lyr in n.lyrics:
                    le = _sub(ne, "lyric")
                    if lyr.syllabic:
                        _sub(le, "syllabic", lyr.syllabic)
                    _sub(le, "text", lyr.text)

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
