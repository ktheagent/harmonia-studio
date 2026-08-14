from __future__ import annotations

import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Type

from .logging_setup import configure_logging


def format_exception_text(exc_type, exc_value, tb) -> str:
    """Return a complete traceback string suitable for logs and diagnostics."""
    return "".join(traceback.format_exception(exc_type, exc_value, tb)).rstrip()


def _write_smoke_report(text: str) -> None:
    report = os.environ.get("HARMONIA_SMOKE_REPORT", "").strip()
    if not report:
        return
    try:
        path = Path(report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    except Exception:
        pass


def _show_error_dialog(message: str, log_path: Path) -> None:
    try:
        from tkinter import messagebox
        messagebox.showerror(
            "Harmonia Studio Error",
            f"{message}\n\nDiagnostic log: {log_path}",
        )
    except Exception:
        pass


def run_tk_app(app_class: Type, *, smoke_env: str = "HARMONIA_STARTUP_SMOKE") -> int:
    """Run a Tk app with startup and callback crash reporting."""
    log_path = configure_logging()
    logger = logging.getLogger("harmonia")
    smoke = os.environ.get(smoke_env, "").strip() == "1"

    try:
        app = app_class()
    except Exception:
        text = format_exception_text(*sys.exc_info())
        logger.error("Fatal application startup error\n%s", text)
        if smoke:
            _write_smoke_report("STARTUP ERROR\n" + text)
        else:
            _show_error_dialog("Harmonia Studio could not start.", log_path)
        return 1

    callback_failed = False

    def report_callback_exception(exc_type, exc_value, tb) -> None:
        nonlocal callback_failed
        callback_failed = True
        text = format_exception_text(exc_type, exc_value, tb)
        logger.error("Unhandled Tk callback exception\n%s", text)
        if smoke:
            _write_smoke_report("TK CALLBACK ERROR\n" + text)
            try:
                app.after_idle(app.destroy)
            except Exception:
                pass
        else:
            _show_error_dialog("An unexpected application error occurred.", log_path)

    app.report_callback_exception = report_callback_exception

    if smoke:
        try:
            delay_ms = max(250, min(10_000, int(os.environ.get("HARMONIA_SMOKE_MS", "1500"))))
        except ValueError:
            delay_ms = 1500
        app.after(delay_ms, app.destroy)

    try:
        app.mainloop()
    except Exception:
        text = format_exception_text(*sys.exc_info())
        logger.error("Fatal Tk main-loop error\n%s", text)
        if smoke:
            _write_smoke_report("MAIN LOOP ERROR\n" + text)
        else:
            _show_error_dialog("Harmonia Studio stopped unexpectedly.", log_path)
        return 1

    if callback_failed:
        return 1
    if smoke:
        _write_smoke_report("OK\nPackaged GUI startup smoke completed successfully.")
    return 0
