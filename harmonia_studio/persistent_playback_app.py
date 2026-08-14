from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .diagnostic_audio_app import DiagnosticAudioHarmoniaApp
from .playback_app import PlaybackHarmoniaApp
from .playback_preferences import clamp_master_volume, scale_part_volumes


class PersistentPlaybackHarmoniaApp(DiagnosticAudioHarmoniaApp):
    """Build-50 layer that persists speaker, master-volume, and loop preferences."""

    def _build_shell(self):
        super()._build_shell()

        # Restore the loop preference into the existing transport control.
        self.playback_loop_var.set(bool(self.settings.loopSelectedMeasure))

        center = self.workspace.master
        panel = ttk.Frame(center)
        panel.pack(fill="x", before=self.workspace_title)

        self.speaker_enabled_var = tk.BooleanVar(value=bool(self.settings.speakerOutputEnabled))
        ttk.Checkbutton(
            panel,
            text="Speaker output",
            variable=self.speaker_enabled_var,
            command=self._save_speaker_preference,
        ).pack(side="left", padx=(4, 8))

        ttk.Label(panel, text="Master volume").pack(side="left", padx=(8, 4))
        self.master_volume_var = tk.DoubleVar(value=clamp_master_volume(self.settings.playbackMasterVolume))
        ttk.Scale(
            panel,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            length=180,
            variable=self.master_volume_var,
            command=self._save_master_volume,
        ).pack(side="left")
        self.master_volume_label = ttk.Label(panel, text=f"{int(round(self.master_volume_var.get() * 100))}%")
        self.master_volume_label.pack(side="left", padx=(4, 8))

    def _save_preferences(self) -> None:
        self.settings_service.save(self.settings)

    def _save_speaker_preference(self) -> None:
        enabled = bool(self.speaker_enabled_var.get())
        self.settings.speakerOutputEnabled = enabled
        if not enabled:
            self.audio_output.stop()
        self._save_preferences()
        self.status_var.set("Speaker output enabled" if enabled else "Speaker output disabled")

    def _save_master_volume(self, value) -> None:
        volume = clamp_master_volume(value)
        self.settings.playbackMasterVolume = volume
        self.master_volume_label.configure(text=f"{int(round(volume * 100))}%")
        self._save_preferences()

    def _apply_loop_setting(self):
        super()._apply_loop_setting()
        self.settings.loopSelectedMeasure = bool(self.playback_loop_var.get())
        self._save_preferences()

    def _current_part_volumes(self) -> dict[int, float]:
        volumes = super()._current_part_volumes()
        return scale_part_volumes(volumes, self.settings.playbackMasterVolume)

    def _play_score(self):
        if not bool(self.settings.speakerOutputEnabled):
            PlaybackHarmoniaApp._play_score(self)
            self.status_var.set("Transport playing with speaker output disabled")
            return
        super()._play_score()

    def _run_speaker_test(self):
        if not bool(self.settings.speakerOutputEnabled):
            self.status_var.set("Enable speaker output before running the speaker test")
            return
        super()._run_speaker_test()


def main():
    from .logging_setup import configure_logging

    configure_logging()
    app = PersistentPlaybackHarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
