from __future__ import annotations

from dataclasses import dataclass, field

from .score import Score


@dataclass(frozen=True)
class PreviewElement:
    kind: str
    coords: tuple[float, ...]
    text: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    width: float = 1.0
    font_size: int = 10
    anchor: str = "center"


@dataclass(frozen=True)
class PreviewLayout:
    width: float
    height: float
    elements: tuple[PreviewElement, ...]


def build_preview_layout(score: Score, *, zoom: float = 1.0, measures_per_row: int = 4) -> PreviewLayout:
    """Build a deterministic, Tk-independent notation preview layout."""
    z = max(0.5, min(3.0, float(zoom)))
    per_row = max(1, int(measures_per_row))
    margin = 30 * z
    measure_w = 210 * z
    staff_gap = 10 * z
    part_row_h = 138 * z
    title_h = 72 * z
    max_measures = max((len(p.measures) for p in score.parts), default=1)
    rows = max(1, (max_measures + per_row - 1) // per_row)
    width = margin * 2 + measure_w * per_row
    height = title_h + margin + max(1, len(score.parts)) * rows * part_row_h + margin
    elements: list[PreviewElement] = [
        PreviewElement("text", (margin, margin), score.title or "Untitled", ("score-title",), font_size=max(12, int(22*z)), anchor="nw")
    ]
    if score.composer:
        elements.append(PreviewElement("text", (width-margin, margin), score.composer, ("score-composer",), font_size=max(9, int(11*z)), anchor="ne"))

    for pi, part in enumerate(score.parts):
        for mi, measure in enumerate(part.measures):
            row, col = divmod(mi, per_row)
            block = pi * rows + row
            x0 = margin + col * measure_w
            y0 = title_h + margin + block * part_row_h
            if col == 0:
                elements.append(PreviewElement("text", (x0, y0-18*z), part.name, ("part-label", f"part:{pi}"), font_size=max(9, int(11*z)), anchor="nw"))
            for line in range(5):
                y = y0 + line * staff_gap
                elements.append(PreviewElement("line", (x0, y, x0+measure_w, y), tags=("staff-line", f"part:{pi}", f"measure:{mi}")))
            elements.append(PreviewElement("line", (x0+measure_w, y0, x0+measure_w, y0+4*staff_gap), tags=("barline", f"measure:{mi}")))
            elements.append(PreviewElement("text", (x0+3*z, y0-5*z), str(measure.number), ("measure-number", f"measure:{mi}"), font_size=max(7, int(8*z)), anchor="sw"))

            for hi, harmony in enumerate(measure.harmonies):
                symbol = harmony.symbol or harmony.root
                if harmony.bass and not harmony.symbol:
                    symbol = f"{harmony.root}/{harmony.bass}"
                elements.append(PreviewElement("text", (x0+(35+hi*48)*z, y0-20*z), symbol, ("harmony", f"measure:{mi}"), font_size=max(8, int(10*z))))

            beats = max(1.0, float(measure.time.beats) * 4.0 / max(1, int(measure.time.beat_type)))
            usable = max(1.0, measure_w-58*z)
            for ni, note in enumerate(measure.notes):
                tag = f"note:{pi}:{mi}:{ni}"
                tags = ("score-note", tag, f"part:{pi}", f"measure:{mi}", f"voice:{note.voice}")
                x = x0 + 42*z + (float(note.onset)/beats)*usable
                if note.pitch is None:
                    elements.append(PreviewElement("rect", (x-5*z, y0+18*z, x+5*z, y0+22*z), tags=tags))
                    continue
                midi = note.pitch.midi()
                y = y0 + 2*staff_gap - (midi-71)*staff_gap/2
                if note.pitch.alter:
                    accidental = "#" if note.pitch.alter > 0 else "b"
                    elements.append(PreviewElement("text", (x-10*z, y), accidental, ("accidental", tag), font_size=max(8, int(10*z)), anchor="e"))
                elements.append(PreviewElement("ellipse", (x-5*z, y-3.5*z, x+5*z, y+3.5*z), tags=tags))
                if note.duration <= 2:
                    elements.append(PreviewElement("line", (x+4*z, y, x+4*z, y-27*z), tags=tags, width=max(1.0, z)))
                lyric = " ".join(l.text for l in note.lyrics if l.text).strip()
                if lyric:
                    elements.append(PreviewElement("text", (x, y0+63*z), lyric, ("lyric", tag), font_size=max(8, int(9*z)), anchor="n"))
    return PreviewLayout(width, height, tuple(elements))
