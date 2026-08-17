from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopTokens:
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 12
    spacing_lg: int = 16
    spacing_xl: int = 24
    sidebar_width: int = 220
    inspector_width: int = 270
    transport_height: int = 54
    min_width: int = 1100
    min_height: int = 700


@dataclass(frozen=True)
class CommandGroup:
    name: str
    commands: tuple[str, ...]


COMMAND_GROUPS = (
    CommandGroup("File", ("New", "Open", "Save")),
    CommandGroup("History", ("Undo", "Redo")),
    CommandGroup("Note", ("Pitch −", "Pitch +", "Delete")),
    CommandGroup("Music", ("Analyze", "Harmonize", "Arrange")),
    CommandGroup("Document", ("Import", "Export")),
)


def toolbar_command_names() -> tuple[str, ...]:
    return tuple(command for group in COMMAND_GROUPS for command in group.commands)


def panel_widths(total_width: int, tokens: DesktopTokens = DesktopTokens()) -> tuple[int, int, int]:
    """Return left, center, right target widths while preserving a useful score viewport."""
    width = max(tokens.min_width, int(total_width))
    left = tokens.sidebar_width
    right = tokens.inspector_width
    center = max(560, width - left - right - (tokens.spacing_md * 2))
    return left, center, right
