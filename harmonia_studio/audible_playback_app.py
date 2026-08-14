from __future__ import annotations

from .audio_output import create_audio_output
from .playback import PlaybackState
from .playback_app import PlaybackHarmoniaApp


class AudiblePlaybackHarmoniaApp(PlaybackHarmoniaApp):
    """Build-48 desktop layer that adds native Windows speaker playback."""

    def __init__(self, *args, **kwargs):
        self.audio_output = create_audio_output()
        super().__init__(*args, **kwargs)

    def _current_part_volumes(self) -> dict[int, float]:
        return dict(self.playback.volumes)

    def _play_score(self):
        score = self.controller.score
        if score is None:
            self.status_var.set("Load a score before playback")
            return
        self._apply_loop_setting()
        start = self._selected_measure_index()
        self.playback.seek_measure(start)
        try:
            loop_measure = start if self.playback.loop_range is not None else None
            self.audio_output.play(
                score,
                start_measure=start,
                loop_measure=loop_measure,
                part_volumes=self._current_part_volumes(),
            )
        except Exception as exc:
            self.status_var.set(f"Speaker playback unavailable: {exc}")
        super()._play_score()

    def _toggle_pause(self):
        state = self.playback.state
        if state == PlaybackState.PLAYING:
            self.audio_output.stop()
            super()._toggle_pause()
            return
        if state == PlaybackState.PAUSED:
            score = self.controller.score
            current = self.playback.cursor_measure
            if score is not None:
                try:
                    loop_measure = current if self.playback.loop_range is not None else None
                    self.audio_output.play(
                        score,
                        start_measure=current,
                        loop_measure=loop_measure,
                        part_volumes=self._current_part_volumes(),
                    )
                except Exception as exc:
                    self.status_var.set(f"Speaker playback unavailable: {exc}")
            super()._toggle_pause()
            return
        super()._toggle_pause()

    def _stop_playback(self):
        self.audio_output.stop()
        super()._stop_playback()

    def _seek_measure(self):
        self.audio_output.stop()
        super()._seek_measure()

    def _after_edit(self, message: str):
        self.audio_output.stop()
        super()._after_edit(message)

    def destroy(self):
        try:
            self.audio_output.close()
        finally:
            super().destroy()


def main():
    from .logging_setup import configure_logging
    configure_logging()
    app = AudiblePlaybackHarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
