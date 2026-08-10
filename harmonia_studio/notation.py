from __future__ import annotations
from dataclasses import dataclass
from html import escape
from .score import Score, Note

@dataclass
class RenderOptions:
    zoom: float = 1.0
    page_mode: bool = True
    measure_width: float = 180.0
    staff_spacing: float = 10.0
    margin: float = 30.0

def _pitch_position(note: Note, staff_mid_y: float, spacing: float) -> float:
    if note.pitch is None:
        return staff_mid_y
    # Treble-oriented reference: B4 sits on middle line.
    midi_delta = note.pitch.midi() - 71
    return staff_mid_y - (midi_delta * spacing / 2.0)

def render_score_svg(score: Score, options: RenderOptions | None = None) -> str:
    o = options or RenderOptions()
    z = max(0.25, min(4.0, o.zoom))
    measure_w = o.measure_width * z
    staff_gap = 120 * z
    margin = o.margin * z
    measures_per_row = 4 if o.page_mode else max(
        1, max((len(p.measures) for p in score.parts), default=1)
    )
    max_measures = max((len(p.measures) for p in score.parts), default=1)
    rows = max(1, (max_measures + measures_per_row - 1) // measures_per_row)
    width = margin * 2 + measure_w * measures_per_row
    height = margin * 2 + max(1, len(score.parts)) * rows * staff_gap + 80 * z

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{margin}" y="{margin}" font-size="{22*z:.1f}" font-family="serif">{escape(score.title)}</text>',
    ]
    if score.composer:
        out.append(
            f'<text x="{width-margin}" y="{margin}" text-anchor="end" font-size="{12*z:.1f}" '
            f'font-family="serif">{escape(score.composer)}</text>'
        )

    for part_index, part in enumerate(score.parts):
        for measure_index, measure in enumerate(part.measures):
            row = measure_index // measures_per_row
            col = measure_index % measures_per_row
            y0 = margin + 70*z + (part_index * rows + row) * staff_gap
            x0 = margin + col * measure_w
            spacing = o.staff_spacing * z
            staff_mid = y0 + 2 * spacing

            if col == 0:
                out.append(
                    f'<text x="{x0}" y="{y0-12*z}" font-size="{11*z:.1f}" '
                    f'font-family="sans-serif">{escape(part.name)}</text>'
                )
                # Simple treble clef label until a full engraving glyph system is added.
                out.append(
                    f'<text x="{x0+4*z}" y="{staff_mid+8*z}" font-size="{28*z:.1f}" '
                    f'font-family="serif">𝄞</text>'
                )

            for line in range(5):
                yy = y0 + line * spacing
                out.append(
                    f'<line x1="{x0}" y1="{yy:.1f}" x2="{x0+measure_w}" y2="{yy:.1f}" '
                    'stroke="black" stroke-width="1"/>'
                )
            out.append(
                f'<line x1="{x0+measure_w}" y1="{y0:.1f}" x2="{x0+measure_w}" '
                f'y2="{y0+4*spacing:.1f}" stroke="black" stroke-width="1"/>'
            )
            out.append(
                f'<text x="{x0+2*z}" y="{y0-2*z}" font-size="{8*z:.1f}" '
                f'font-family="sans-serif">{measure.number}</text>'
            )

            for hidx, harmony in enumerate(measure.harmonies):
                symbol = harmony.symbol or (harmony.root + (("/"+harmony.bass) if harmony.bass else ""))
                out.append(
                    f'<text x="{x0+35*z+hidx*50*z}" y="{y0-15*z}" font-size="{12*z:.1f}" '
                    f'font-weight="bold" font-family="sans-serif">{escape(symbol)}</text>'
                )

            beats_in_measure = max(1.0, measure.time.beats * 4.0 / measure.time.beat_type)
            for note in measure.notes:
                x = x0 + 38*z + (note.onset / beats_in_measure) * max(1.0, measure_w-45*z)
                y = _pitch_position(note, staff_mid, spacing)
                if note.is_rest:
                    out.append(
                        f'<rect x="{x-4*z:.1f}" y="{staff_mid-2*z:.1f}" width="{8*z:.1f}" '
                        f'height="{4*z:.1f}" fill="black"/>'
                    )
                else:
                    out.append(
                        f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{5*z:.1f}" ry="{3.6*z:.1f}" '
                        'fill="black" transform="rotate(-15 '
                        f'{x:.1f} {y:.1f})"/>'
                    )
                    if note.duration <= 2.0:
                        out.append(
                            f'<line x1="{x+4*z:.1f}" y1="{y:.1f}" x2="{x+4*z:.1f}" '
                            f'y2="{y-28*z:.1f}" stroke="black" stroke-width="{1.2*z:.1f}"/>'
                        )
                if note.lyrics:
                    text = " ".join(l.text for l in note.lyrics if l.text)
                    if text:
                        out.append(
                            f'<text x="{x:.1f}" y="{y0+65*z:.1f}" text-anchor="middle" '
                            f'font-size="{10*z:.1f}" font-family="sans-serif">{escape(text)}</text>'
                        )
    out.append("</svg>")
    return "\n".join(out)
