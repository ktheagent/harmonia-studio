from __future__ import annotations

from .crash_reporting import run_tk_app
from .menu_safe_app import MenuSafeHarmoniaApp


def main() -> int:
    return run_tk_app(MenuSafeHarmoniaApp)


if __name__ == "__main__":
    raise SystemExit(main())
