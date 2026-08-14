from __future__ import annotations

import math


def clamp_master_volume(value) -> float:
    try:
        volume = float(value)
    except (TypeError, ValueError):
        return 1.0
    if not math.isfinite(volume):
        return 1.0
    return max(0.0, min(1.0, volume))


def scale_part_volumes(volumes: dict[int, float], master_volume: float) -> dict[int, float]:
    master = clamp_master_volume(master_volume)
    return {index: max(0.0, min(1.0, float(volume)) * master) for index, volume in volumes.items()}
