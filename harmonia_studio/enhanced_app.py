from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk

from .app import HarmoniaApp
from .desktop_preview import build_preview_layout
from .editor import ScoreEditor
from .logging_setup import configure_logging


class EnhancedHarmoniaApp(HarmoniaApp):
    """Desktop workspace with native notation preview and basic score editing."""

    def __init__(self, *args, **kwargs):
        self.score_editor: ScoreEditor | None = None
        self.selected_note: tuple[int, int, int] | None = None
        self.preview_zoom = 1.0
        super().__init__(*args, **kwargs)

    def _build_menu(self):
        super()._build_menu()
        menubar = self.nametowidget(self.cget("menu"))
        for i in range(menubar.index("end") + 1):
            if menubar.entrycget(i, "label") != "Edit":
                continue
            edit = self.nametowidget(menubar.entrycget(i, "menu"))
            for j in range(edit.index("end") + 1):
                label = edit.entrycget(j, "label")
                if label == "Undo":
                    edit.entryconfigure(j, state="normal", command=self._undo_edit)
                elif label == "Redo":
                    edit.entryconfigure(j, state="normal", command=self._redo_edit)
            break

    def _build_shell(self):
        super()._build_shell()
        center = self.workspace.master
        self.workspace.destroy()

        controls = ttk.Frame(center)
        controls.pack(fill="x", before=self.workspace_title)
        ttk.Button(controls, text="Undo", command=self._undo_edit).pack(side="left", padx=2)
        ttk.Button(controls, text="Redo", command=self._redo_edit).pack(side="left", padx=2)
        ttk.Separator(controls, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(controls, text="Pitch −", command=lambda: self._transpose_selected(-1)).pack(side="left", padx=2)
        ttk.Button(controls, text="Pitch +", command=lambda: self._transpose_selected(1)).pack(side="left", padx=2)
        ttk.Button(controls, text="Delete Note", command=self._delete_selected).pack(side="left", padx=2)
        ttk.Separator(controls, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(controls, text="Zoom −", command=lambda: self._change_zoom(-0.1)).pack(side="left", padx=2)
        ttk.Button(controls, text="Zoom +", command=lambda: self._change_zoom(0.1)).pack(side="left", padx=2)

        viewport = ttk.Frame(center)
        viewport.pack(fill="both", expand=True)
        self.preview_canvas = tk.Canvas(viewport, background="white", highlightthickness=0)
        xbar = ttk.Scrollbar(viewport, orient="horizontal", command=self.preview_canvas.xview)
        ybar = ttk.Scrollbar(viewport, orient="vertical", command=self.preview_canvas.yview)
        self.preview_canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        viewport.rowconfigure(0, weight=1)
        viewport.columnconfigure(0, weight=1)
        self.workspace = self.preview_canvas
        self.preview_canvas.bind("<Button-1>", self._canvas_click)
        self.bind_all("<Control-z>", lambda _e: self._undo_edit())
        self.bind_all("<Control-y>", lambda _e: self._redo_edit())

    def _ensure_editor(self):
        score = self.controller.score
        if score is None:
            self.score_editor = None
            self.selected_note = None
            return None
        if self.score_editor is None or self.score_editor.score is not score:
            self.score_editor = ScoreEditor(score)
            self.selected_note = None
        return self.score_editor

    def _refresh_workspace(self):
        score = self.controller.score
        self.parts_list.delete(0, "end")
        self.preview_canvas.delete("all")
        if score is None:
            self.workspace_title.configure(text="Welcome to Harmonia Studio")
            self.preview_canvas.create_text(
                40, 40, anchor="nw",
                text="Create or open a project, then choose File → Import Music.\n\nImported and generated scores appear here as editable notation.",
                font=("TkDefaultFont", 12),
            )
            self.preview_canvas.configure(scrollregion=(0, 0, 900, 600))
            self._set_text(self.inspector, "No score loaded.")
            self._ensure_editor()
            return

        self._ensure_editor()
        self.workspace_title.configure(text=score.title or "Untitled Score")
        for part in score.parts:
            self.parts_list.insert("end", f"{part.name}  ({len(part.measures)} measures)")
        layout = build_preview_layout(score, zoom=self.preview_zoom)
        for e in layout.elements:
            if e.kind == "line":
                self.preview_canvas.create_line(*e.coords, width=e.width, tags=e.tags)
            elif e.kind == "rect":
                self.preview_canvas.create_rectangle(*e.coords, fill="black", outline="black", tags=e.tags)
            elif e.kind == "ellipse":
                self.preview_canvas.create_oval(*e.coords, fill="black", outline="black", tags=e.tags)
            elif e.kind == "text":
                self.preview_canvas.create_text(*e.coords, text=e.text, anchor=e.anchor, font=("TkDefaultFont", e.font_size), tags=e.tags)
        self.preview_canvas.configure(scrollregion=(0, 0, layout.width, layout.height))
        if self.selected_note is not None:
            self._highlight_selection()
            self._show_selected()
        else:
            notes = sum(1 for n in score.iter_notes() if n.pitch is not None)
            measures = max((len(p.measures) for p in score.parts), default=0)
            self._set_text(self.inspector, f"Score: {score.title}\nComposer: {score.composer or '—'}\nParts: {len(score.parts)}\nMeasures: {measures}\nPitched notes: {notes}\n\nClick a notehead to edit it.")

    def _canvas_click(self, _event):
        current = self.preview_canvas.find_withtag("current")
        tag = None
        if current:
            tag = next((t for t in self.preview_canvas.gettags(current[0]) if t.startswith("note:")), None)
        if tag:
            try:
                _, p, m, n = tag.split(":")
                self.selected_note = (int(p), int(m), int(n))
            except ValueError:
                self.selected_note = None
        else:
            self.selected_note = None
        self._refresh_workspace()

    def _selected_object(self):
        if self.selected_note is None or self.controller.score is None:
            return None
        p, m, n = self.selected_note
        try:
            return self.controller.score.parts[p].measures[m].notes[n]
        except IndexError:
            self.selected_note = None
            return None

    def _highlight_selection(self):
        if self.selected_note is None:
            return
        tag = "note:" + ":".join(str(v) for v in self.selected_note)
        box = self.preview_canvas.bbox(tag)
        if box:
            x1, y1, x2, y2 = box
            self.preview_canvas.create_rectangle(x1-4, y1-4, x2+4, y2+4, outline="black", width=2, dash=(4, 2))

    def _show_selected(self):
        note = self._selected_object()
        if note is None:
            return
        pitch = "Rest" if note.pitch is None else f"{note.pitch.step}{'#' * max(0,note.pitch.alter)}{'b' * max(0,-note.pitch.alter)}{note.pitch.octave}"
        midi = "—" if note.pitch is None else str(note.pitch.midi())
        lyrics = " ".join(l.text for l in note.lyrics if l.text) or "—"
        self._set_text(self.inspector, f"Selected note\n\nPitch: {pitch}\nMIDI: {midi}\nDuration: {note.duration:g} beats\nOnset: {note.onset:g}\nVoice: {note.voice}\nStaff: {note.staff}\nLyrics: {lyrics}")

    def _after_edit(self, message: str):
        self._sync_project_score()
        self.status_var.set(message)
        self._refresh_workspace()

    def _transpose_selected(self, semitones: int):
        editor = self._ensure_editor()
        note = self._selected_object()
        if editor is None or self.selected_note is None or note is None or note.pitch is None:
            self.status_var.set("Select a pitched note first")
            return
        editor.move_pitch(*self.selected_note, semitones)
        self._after_edit(f"Moved selected note {semitones:+d} semitone(s)")

    def _delete_selected(self):
        editor = self._ensure_editor()
        if editor is none or self.selected_note is None:
            self.status_var.set("Select a note first")
            return
        p, m, n = self.selected_note
        editor.remove_note(p, m, n)
        self.selected_note = None
        self._after_edit("Deleted selected note")

    def _undo_edit(self):
        editor = self._ensure_editor()
        if editor is not None and editor.undo():
            self.selected_note = None
            self._after_edit("Undo")
        else:
            self.status_var.set("Nothing to undo")

    def _redo_edit(self):
        editor = self._ensure_editor()
        if editor is not None and editor.redo():
            self.selected_note = None
            self._after_edit("Redo")
        else:
            self.status_var.set("Nothing to redo")

    def _change_zoom(self, delta: float):
        self.preview_zoom = max(0.5, min(3.0, round(self.preview_zoom + delta, 2)))
        self.status_var.set(f"Notation zoom: {self.preview_zoom:.1f}×")
        self._refresh_workspace()


def main():
    configure_logging()
    logging.getLogger("harmonia").info("Starting Harmonia Studio enhanced desktop workspace")
    app = EnhancedHarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
