from __future__ import annotations

from queue import Empty, SimpleQueue
import tkinter as tk
from tkinter import ttk

from .desktop_preview import build_preview_layout
from .playback import PlaybackEngine, PlaybackEvent, PlaybackState
from .playback_workspace import measure_tag, note_tag, parse_measure_value
from .rich_editing_app import RichEditingHarmoniaApp


class PlaybackHarmoniaApp(RichEditingHarmoniaApp):
    """Build-47 workspace with transport controls and score-position highlighting."""

    def __init__(self, *args, **kwargs):
        self._playback_events: SimpleQueue[PlaybackEvent] = SimpleQueue()
        self.playback = PlaybackEngine(self._enqueue_playback_event)
        self._playback_highlight_ids: list[int] = []
        self._playback_poll_id = None
        super().__init__(*args, **kwargs)
        self._schedule_playback_poll()

    def _build_shell(self):
        super()._build_shell()
        center = self.workspace.master
        transport = ttk.Frame(center)
        transport.pack(fill="x", before=self.workspace_title)

        ttk.Button(transport, text="Play", command=self._play_score).pack(side="left", padx=2)
        ttk.Button(transport, text="Pause/Resume", command=self._toggle_pause).pack(side="left", padx=2)
        ttk.Button(transport, text="Stop", command=self._stop_playback).pack(side="left", padx=2)

        ttk.Label(transport, text="Measure").pack(side="left", padx=(10, 2))
        self.playback_measure_var = tk.StringVar(value="1")
        ttk.Entry(transport, textvariable=self.playback_measure_var, width=5).pack(side="left")
        ttk.Button(transport, text="Seek", command=self._seek_measure).pack(side="left", padx=2)

        self.playback_loop_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            transport,
            text="Loop selected measure",
            variable=self.playback_loop_var,
            command=self._apply_loop_setting,
        ).pack(side="left", padx=(10, 2))

        self.playback_position_var = tk.StringVar(value="Stopped")
        ttk.Label(transport, textvariable=self.playback_position_var).pack(side="right", padx=6)

    def _enqueue_playback_event(self, event: PlaybackEvent):
        self._playback_events.put(event)

    def _schedule_playback_poll(self):
        try:
            self._playback_poll_id = self.after(25, self._poll_playback_events)
        except tk.TclError:
            self._playback_poll_id = None

    def _poll_playback_events(self):
        latest = None
        try:
            while True:
                latest = self._playback_events.get_nowait()
        except Empty:
            pass
        if latest is not None:
            self._highlight_playback_event(latest)
        if self.playback.state == PlaybackState.STOPPED and latest is None:
            if self.playback_position_var.get().startswith(("Playing", "Paused")):
                self.playback_position_var.set("Stopped")
        self._schedule_playback_poll()

    def _play_score(self):
        score = self.controller.score
        if score is None:
            self.status_var.set("Load a score before playback")
            return
        self._apply_loop_setting()
        start = self._selected_measure_index()
        self.playback.seek_measure(start)
        self.playback.play(score, start_measure=start)
        self.playback_position_var.set(f"Playing measure {start + 1}")
        self.status_var.set("Playback transport started (visual/MIDI sink; no speaker backend claimed)")

    def _toggle_pause(self):
        if self.playback.state == PlaybackState.PLAYING:
            self.playback.pause()
            self.playback_position_var.set(f"Paused at measure {self.playback.cursor_measure + 1}")
        elif self.playback.state == PlaybackState.PAUSED:
            self.playback.resume()
            self.playback_position_var.set(f"Playing measure {self.playback.cursor_measure + 1}")

    def _stop_playback(self):
        self.playback.stop()
        self._clear_playback_highlight()
        self.playback_position_var.set("Stopped")

    def _selected_measure_index(self) -> int:
        score = self.controller.score
        count = max((len(p.measures) for p in score.parts), default=0) if score is not None else 0
        if self.selected_note is not None:
            return max(0, min(count - 1, self.selected_note[1])) if count else 0
        return parse_measure_value(self.playback_measure_var.get(), count)

    def _seek_measure(self):
        target = self._selected_measure_index()
        self.playback.seek_measure(target)
        self.playback_measure_var.set(str(target + 1))
        self.playback_position_var.set(f"Ready at measure {target + 1}")
        self._highlight_measure(target)

    def _apply_loop_setting(self):
        if self.playback_loop_var.get():
            measure = self._selected_measure_index()
            self.playback.set_loop(measure, measure)
        else:
            self.playback.set_loop(None)

    def _after_edit(self, message: str):
        # Editing invalidates the active event schedule. Stop first, then let the
        # editor synchronize the project and redraw the score.
        if self.playback.state != PlaybackState.STOPPED:
            self._stop_playback()
        super()._after_edit(message)

    def _clear_playback_highlight(self):
        for item_id in self._playback_highlight_ids:
            try:
                self.preview_canvas.delete(item_id)
            except tk.TclError:
                pass
        self._playback_highlight_ids.clear()

    def _highlight_measure(self, measure_index: int):
        self._clear_playback_highlight()
        box = self.preview_canvas.bbox(measure_tag(measure_index))
        if box:
            x1, y1, x2, y2 = box
            self._playback_highlight_ids.append(
                self.preview_canvas.create_rectangle(
                    x1 - 5, y1 - 5, x2 + 5, y2 + 5, outline="black", width=2, dash=(8, 4)
                )
            )

    def _highlight_playback_event(self, event: PlaybackEvent):
        self._clear_playback_highlight()
        box = self.preview_canvas.bbox(note_tag(event))
        if box:
            x1, y1, x2, y2 = box
            self._playback_highlight_ids.append(
                self.preview_canvas.create_rectangle(
                    x1 - 4, y1 - 4, x2 + 4, y2 + 4, outline="black", width=3
                )
            )
            self.preview_canvas.xview_moveto(max(0.0, (x1 - 80) / max(1.0, float(self.preview_canvas.bbox("all")[2]))))
        self.playback_measure_var.set(str(event.measure_index + 1))
        self.playback_position_var.set(
            f"Playing measure {event.measure_index + 1} · MIDI {event.midi}"
        )

    def _refresh_workspace(self):
        """Safe native-canvas redraw used by build 47.

        This intentionally owns the draw path instead of calling the older
        enhanced-app redraw branch, keeping playback highlighting deterministic.
        """
        score = self.controller.score
        self.parts_list.delete(0, "end")
        self.preview_canvas.delete("all")
        self._playback_highlight_ids.clear()

        if score is None:
            self.workspace_title.configure(text="Welcome to Harmonia Studio")
            self.preview_canvas.create_text(
                40, 40, anchor="nw",
                text="Create or open a project, then choose File → Import Music.",
                font=("TkDefaultFont", 12),
            )
            self.preview_canvas.configure(scrollregion=(0, 0, 900, 600))
            self._set_text(self.inspector, "No score loaded.")
            self._ensure_editor()
            return

        self._ensure_editor()
        self.workspace_title.configure(text=score.title or "Untitled Score")
        for part in score.parts:
            self.parts_list.insert("end", f"{part.name} ({len(part.measures)} measures)")

        layout = build_preview_layout(score, zoom=self.preview_zoom)
        for element in layout.elements:
            if element.kind == "line":
                self.preview_canvas.create_line(*element.coords, width=element.width, tags=element.tags)
            elif element.kind == "rect":
                self.preview_canvas.create_rectangle(
                    *element.coords, fill="black", outline="black", tags=element.tags
                )
            elif element.kind == "ellipse":
                self.preview_canvas.create_oval(
                    *element.coords, fill="black", outline="black", tags=element.tags
                )
            elif element.kind == "text":
                self.preview_canvas.create_text(
                    *element.coords,
                    text=element.text,
                    anchor=element.anchor,
                    font=("TkDefaultFont", element.font_size),
                    tags=element.tags,
                )
        self.preview_canvas.configure(scrollregion=(0, 0, layout.width, layout.height))

        if self.selected_note is not None:
            self._highlight_selection()
            self._show_selected()
        else:
            pitched = sum(1 for note in score.iter_notes() if note.pitch is not None)
            measures = max((len(part.measures) for part in score.parts), default=0)
            self._set_text(
                self.inspector,
                f"Score: {score.title}\nComposer: {score.composer or '—'}\n"
                f"Parts: {len(score.parts)}\nMeasures: {measures}\nPitched notes: {pitched}\n\n"
                "Click a notehead to edit it.",
            )

    def destroy(self):
        self.playback.stop()
        if self._playback_poll_id is not None:
            try:
                self.after_cancel(self._playback_poll_id)
            except tk.TclError:
                pass
        super().destroy()


def main():
    from .logging_setup import configure_logging
    configure_logging()
    app = PlaybackHarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
