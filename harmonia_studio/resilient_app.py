from __future__ import annotations

from .crash_reporting import run_tk_app
from .persistent_playback_app import PersistentPlaybackHarmoniaApp


def main() -> int:
    return run_tk_app(PersistentPlaybackHarmoniaApp)


if __name__ == "__main__":
    raise SystemExit(main())
