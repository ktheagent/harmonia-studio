from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .audio_diagnostics import build_speaker_test_score, inspect_audio_output
from .audible_playback_app import AudiblePlaybackHarmoniaApp


class DiagnosticAudioHarmoniaApp(AudiblePlaybackHarmoniaApp):
    """Build-49 layer exposing audio backend state and an end-to-end speaker self-test."""

    def _build_shell(self):
        super()._build_shell()
        center = self.workspace.master

        panel = ttk.Frame(center)
        panel.pack(fill="x", before=self.workspace_title)

        status = inspect_audio_output(self.audio_output)
        self.audio_backend_status_var = tk.StringVar(value=f"Audio: {status.summary}")
        ttk.Label(panel, textvariable=self.audio_backend_status_var).pack(side="left", padx=(4, 8))
        ttk.Button(panel, text="Speaker Test", command=self._run_speaker_test).pack(side="left", padx=2)
        ttk.Button(panel, text="Refresh Audio Status", command=self._refresh_audio_status).pack(side="left", padx=2)

    def _refresh_audio_status(self):
        status = inspect_audio_output(self.audio_output)
        self.audio_backend_status_var.set(f"Audio: {status.summary}")
        self.status_var.set(status.summary)

    def _run_speaker_test(self):
        status = inspect_audio_output(self.audio_output)
        if not status.available:
            self.audio_backend_status_var.set(f"Audio: {status.summary}")
            self.status_var.set(status.detail)
            return

        try:
            self.audio_output.stop()
            self.audio_output.play(build_speaker_test_score(), start_measure=0)
            self.audio_backend_status_var.set("Audio: speaker test playing A4")
            self.status_var.set("Speaker self-test started through the normal WAV/Windows audio path")
            self.after(900, self._finish_speaker_test)
        except Exception as exc:
            self.audio_backend_status_var.set(f"Audio: self-test failed — {exc}")
            self.status_var.set(f"Speaker self-test failed: {exc}")

    def _finish_speaker_test(self):
        try:
            self.audio_output.stop()
        finally:
            self._refresh_audio_status()


def main():
    from .logging_setup import configure_logging

    configure_logging()
    app = DiagnosticAudioHarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
