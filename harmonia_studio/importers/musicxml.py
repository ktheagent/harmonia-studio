from __future__ import annotations
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch, Harmony, TimeSignature, KeySignature, Lyric

class MusicXMLImportError(ValueError):
    pass

def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]

def _children(el, name):
    return [x for x in list(el) if _local(x.tag) == name]

def _child(el, name):
    if el is None:
        return None
    for x in list(el):
        if _local(x.tag) == name:
            return x
    return None

def _text(el, name, default=""):
    x = _child(el, name)
    return (x.text or default).strip() if x is not None else default

def _load_xml(path: Path) -> bytes:
    if path.suffix.lower() == ".mxl":
        with zipfile.ZipFile(path) as z:
            rootfile = None
            try:
                container = ET.fromstring(z.read("META-INF/container.xml"))
                for e in container.iter():
                    if _local(e.tag) == "rootfile":
                        rootfile = e.attrib.get("full-path")
                        break
            except KeyError:
                pass
            if not rootfile:
                names = [n for n in z.namelist()
                         if n.lower().endswith((".musicxml", ".xml"))
                         and not n.startswith("META-INF/")]
                if not names:
                    raise MusicXMLImportError("MXL contains no score XML")
                rootfile = names[0]
            return z.read(rootfile)
    return path.read_bytes()

def _duration_divisions(el) -> float:
    try:
        return float(_text(el, "duration", "0") or 0)
    except ValueError:
        return 0.0

def import_musicxml(path: str | Path) -> Score:
    p = Path(path)
    root = ET.fromstring(_load_xml(p))
    if _local(root.tag) != "score-partwise":
        if _local(root.tag) == "score-timewise":
            raise MusicXMLImportError("score-timewise is not yet supported")
        raise MusicXMLImportError("Not a MusicXML score")
    work = _child(root, "work")
    title = _text(work, "work-title", "") or _text(root, "movement-title", "") or p.stem
    composer = ""
    identification = _child(root, "identification")
    if identification is not None:
        for creator in _children(identification, "creator"):
            if creator.attrib.get("type") == "composer" or not composer:
                composer = (creator.text or "").strip()
    part_names = {}
    part_list = _child(root, "part-list")
    if part_list is not None:
        for sp in _children(part_list, "score-part"):
            part_names[sp.attrib.get("id", "")] = _text(sp, "part-name", "Part")

    parts = []
    for pe in _children(root, "part"):
        pid = pe.attrib.get("id", "P1")
        measures = []
        divisions = 1.0
        current_time = TimeSignature()
        current_key = KeySignature()
        tempo = 120.0
        for me in _children(pe, "measure"):
            number_text = me.attrib.get("number", "")
            num = int(number_text) if number_text.isdigit() else len(measures) + 1
            attrs = _child(me, "attributes")
            if attrs is not None:
                try:
                    divisions = float(_text(attrs, "divisions", "1") or "1")
                except ValueError:
                    divisions = 1.0
                time_el = _child(attrs, "time")
                if time_el is not None:
                    current_time = TimeSignature(
                        int(_text(time_el, "beats", "4")),
                        int(_text(time_el, "beat-type", "4")),
                    )
                key_el = _child(attrs, "key")
                if key_el is not None:
                    current_key = KeySignature(
                        int(_text(key_el, "fifths", "0")),
                        _text(key_el, "mode", "major") or "major",
                    )
            for direction in _children(me, "direction"):
                sound = _child(direction, "sound")
                if sound is not None and "tempo" in sound.attrib:
                    try:
                        tempo = float(sound.attrib["tempo"])
                    except ValueError:
                        pass

            notes = []
            harmonies = []
            cursor_divisions = 0.0
            last_onset_by_voice = {}

            for child in list(me):
                tag = _local(child.tag)
                if tag == "harmony":
                    root_el = _child(child, "root")
                    root_step = _text(root_el, "root-step", "")
                    root_alter = _text(root_el, "root-alter", "0")
                    try:
                        alter_int = int(float(root_alter or 0))
                    except ValueError:
                        alter_int = 0
                    if root_step and alter_int:
                        root_step += "#" if alter_int > 0 else "b"
                    kind_el = _child(child, "kind")
                    kind = (kind_el.text or "major").strip() if kind_el is not None else "major"
                    bass_el = _child(child, "bass")
                    bass = _text(bass_el, "bass-step", "")
                    bass_alter = _text(bass_el, "bass-alter", "0")
                    try:
                        bass_alter_int = int(float(bass_alter or 0))
                    except ValueError:
                        bass_alter_int = 0
                    if bass and bass_alter_int:
                        bass += "#" if bass_alter_int > 0 else "b"
                    symbol = (kind_el.attrib.get("text", "") if kind_el is not None else "") or root_step
                    harmonies.append(Harmony(root_step, kind, bass, symbol))
                elif tag == "backup":
                    cursor_divisions = max(0.0, cursor_divisions - _duration_divisions(child))
                elif tag == "forward":
                    cursor_divisions += _duration_divisions(child)
                elif tag == "note":
                    try:
                        voice = int(_text(child, "voice", "1") or 1)
                    except ValueError:
                        voice = 1
                    duration_divisions = _duration_divisions(child)
                    duration = duration_divisions / max(divisions, 1e-9)
                    try:
                        staff = int(_text(child, "staff", "1") or 1)
                    except ValueError:
                        staff = 1
                    pitch = None
                    if _child(child, "rest") is None:
                        pitch_el = _child(child, "pitch")
                        if pitch_el is not None:
                            pitch = Pitch(
                                _text(pitch_el, "step", "C"),
                                int(_text(pitch_el, "octave", "4")),
                                int(float(_text(pitch_el, "alter", "0") or 0)),
                            )
                    lyrics = [
                        Lyric(_text(le, "text", ""), _text(le, "syllabic", ""))
                        for le in _children(child, "lyric")
                    ]
                    ties = _children(child, "tie")
                    is_chord = _child(child, "chord") is not None
                    if is_chord:
                        onset_divisions = last_onset_by_voice.get(voice, cursor_divisions)
                    else:
                        onset_divisions = cursor_divisions
                        last_onset_by_voice[voice] = onset_divisions
                        cursor_divisions += duration_divisions
                    notes.append(
                        Note(
                            pitch=pitch,
                            duration=duration,
                            voice=voice,
                            staff=staff,
                            dots=len(_children(child, "dot")),
                            tie_start=any(t.attrib.get("type") == "start" for t in ties),
                            tie_stop=any(t.attrib.get("type") == "stop" for t in ties),
                            lyrics=lyrics,
                            onset=onset_divisions / max(divisions, 1e-9),
                        )
                    )
            measures.append(
                Measure(
                    num,
                    notes,
                    harmonies,
                    TimeSignature(current_time.beats, current_time.beat_type),
                    KeySignature(current_key.fifths, current_key.mode),
                    tempo,
                )
            )

        parts.append(
            Part(pid, part_names.get(pid, pid), Instrument(part_names.get(pid, "Piano")), measures)
        )
    return Score(title, composer, parts, {"sourceFormat": "MusicXML", "sourcePath": str(p)})
