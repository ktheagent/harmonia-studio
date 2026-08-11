from __future__ import annotations

from dataclasses import dataclass, field

from .score import Score


@dataclass(frozen=True)
class PreviewElement:
    kind: str
    coords: tuple[float, ...]
    text: str = ""
    font_size: float = 10.0
    anchor: str = "center"
    tags: tuple[str, ...] = field(default_factory=tuple)
    width: float = 1.0


@dataclass(frozen=True)
class PreviewLayout:
    width: float
    height: float
    elements: tuple[PreviewElement, ...]


def _pitch_y(midi: int, staff_mid_y: float, spacing: float) -> float:
    # B4 (MIDI 71) sits on the middle line in this preview coordinate system.
    return staff_mid_y - (midi - 71) * spacing / 2.0


def _accidental_text(alter: int) -> str:
    if alter == 1:
        return "#"
    if alter == -1:
        return "b"
    if alter == 2:
        return "x"
    if alter == -2:
        return "bb"
    return ""


def build_preview_layout(
    score: Score,
    *,
    zoom: float = 1.0,
    measures_per_row: int = 4,
) -> PreviewLayout:
    """Build a deterministic, Tk-independent notation preview model.

    The desktop UI consumes this model to draw a native canvas preview. Keeping
    layout outside Tk makes note placement and selectable note references
    regression-testable in headless CI.
    """
    z = max(0.5, min(3.0, float(zoom)))
    per_row = max(1, int(measures_per_row))
    margin = 30.0 * z
    measure_w = 210.0 * z
    staff_spacing = 10.0 * z
    staff_block_h = 138.0 * z
    title_h = 78.0 * z

    max_measures = max((len(part.measures) for part in score.parts), default=1)
    rows = max(1, (max_measures + per_row - 1) // per_row)
    width = margin * 2 + measure_w * per_row
    height = title_h + margin + max(1, len(score.parts)) * rows * staff_block_h + margin

    elements: list[PreviewElement] = [
        PreviewElement(
            "text",
            (margin, margin),
            score.title or "Untitled",
            font_size=22.0 * z,
            anchor="nw",
            tags=("score-title",),
        )
    ]
    if score.composer:
        elements.append(
            PreviewElement(
                "text",
                (width - margin, margin + 4.0 * z),
                score.composer,
                font_size=12.0 * z,
                anchor="ne",
                tags=("score-composer",),
            )
        )

    for part_index, part in enumerate(score.parts):
        for measure_index, measure in enumerate(part.measures):
            row = measure_index // per_row
            col = measure_index % per_row
            block_index = part_index * rows + row
            x0 = margin + col * measure_w
            y0 = title_h + margin + block_index * staff_block_h
            staff_mid = y0 + 2.0 * staff_spacing

            if col == 0:
                elements.append(
                    PreviewElement(
                        "text",
                        (x0, y0 - 18.0 * z),
                        part.name,
                        font_size=11.0 * z,
                        anchor="nw",
                        tags=("part-label", f"part:{part_index}"),
                    )
                )

            for line_index in range(5):
                y = y0 + line_index * staff_spacing
                elements.append(
                    PreviewElement(
                        "line",
                        (x0, y, x0 + measure_w, y),
                        width=max(1.0, z),
                        tags=("staff-line", f"part:{part_index}", f"measure:{measure_index}"),
                    )
                )
            elements.append(
                PreviewElement(
                    "line",
                    (x0 + measure_w, y0, x0 + measure_w, y0 + 4.0 * staff_spacing),
                    width=max(1.0, z),
                    tags=("barline", f"measure:{measure_index}"),
                )
            )
            elements.append(
                PreviewElement(
                    "text",
                    (x0 + 3.0 * z, y0 - 5.0 * z),
                    str(measure.number),
                    font_size=8.0 * z,
                    anchor="sw",
                    tags=("measure-number", f"measure:{measure_index}"),
                )
            )

            harmony_count = max(1, len(measure.harmonies))
            for harmony_index, harmony in enumerate(measure.harmonies):
                symbol = harmony.symbol or harmony.root
                if harmony.bass:
                    symbol = harmony.symbol or f"{harmony.root}/{harmony.bass}"
                hx = x0 + 35.0 * z + harmony_index * max(
                    42.0 * z,
                    (measure_w - 55.0 * z) / harmony_count,
                )
                elements.append(
                    PreviewElement(
                        "text",
                        (hx, y0 - 20.0 * z),
                        symbol,
                        font_size=11.0 * z,
                        anchor="center",
                        tags=("harmony", f"measure:{measure_index}"),
                    )
                )

            beats_in_measure = max(
                1.0,
                float(measure.time.beats) * 4.0 / max(1, int(measure.time.beat_type)),
            )
            usable_w = max(1.0, measure_w - 58.0 * z)

            for note_index, note in enumerate(measure.notes):
                note_tag = f"note:{part_index}:{measure_index}:{note_index}"
                tags = (
                    "score-note",
                    note_tag,
                    f"part:{part_index}",
                    f"measure:{measure_index}",
                    f"voice:{note.voice}",
                )
                x = x0 + 42.0 * z + (float(note.onset) / beats_in_measure) * usable_w

                if note.is_rest:
                    elements.append(
                        PreviewElement(
                            "rect",
                            (x - 5.0 * z, staff_mid - 2.0 * z, x + 5.0 * z, staff_mid + 2.0 * z),
                            tags=tags,
                        )
                    )
                    continue

                y = _pitch_y(note.pitch.midi(), staff_mid, staff_spacing)

                # Short ledger lines keep notes outside the five-line staff readable.
                top_y = y0
                bottom_y = y0 + 4.0 * staff_spacing
                ledger_y = y
                while ledger_y < top_y - staff_spacing / 2.0:
                    elements.append(
                        PreviewElement(
                            "line",
                            (x - 8.0 * z, ledger_y, x + 8.0 * z, ledger_y),
                            width=max(1.0, z),
                            tags=("ledger-line", note_tag),
                        )
                    )
                    ledger_y += staff_spacing
                ledger_y = y
                while ledger_y > bottom_y + staff_spacing / 2.0:
                    elements.append(
                        PreviewElement(
                            "line",
                            (x - 8.0 * z, ledger_y, x + 8.0 * z, ledger_y),
                            width=max(1.0, z),
                            tags=("ledger-line", note_tag),
                        )
                    )
                    ledger_y -= staff_spacing

                accidental = _accidental_text(note.pitch.alter)
                if accidental:
                    elements.append(
                        PreviewElement(
                            "text",
                            (x - 11.0 * z, y),
                            accidental,
                            font_size=11.0 * z,
                            anchor="e",
                            tags=("accidental", note_tag),
                        )
                    )

                elements.append(
                    PreviewElement(
                        "ellipse",
                        (x - 5.0 * z, y - 3.6 * z, x + 5.0 * z, y + 3.6 * z),
                        tags=tags,
                    )
                )
                if note.duration <= 2.0:
                    elements.append(
                        PreviewElement(
                            "line",
                            (x + 4.0 * z, y, x + 4.0 * z, y - 28.0 * z),
                            width=max(1.0, 1.2 * z),
                            tags=tags,
                        )
                    )

                lyric_text = " ".join(lyric.text for lyric in note.lyrics if lyric.text).strip()
                if lyric_text:
                    elements.append(
                        PreviewElement(
                            "text",
                            (x, y0 + 63.0 * z),
                            lyric_text,
                            font_size=9.0 * z,
                            anchor="n",
                            tags=("lyric", note_tag),
                        )
                    )

    return PreviewLayout(width=width, height=height, elements=tuple(elements))
