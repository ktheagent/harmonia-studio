from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from .enhanced_app import EnhancedHarmoniaApp
from .desktop_editing import parse_harmony_symbol, validate_duration

class RichEditingHarmoniaApp(EnhancedHarmoniaApp):
    """Build-46 desktop layer exposing duration, lyrics, harmony and measure editing."""
    def _build_shell(self):
        super()._build_shell()
        # EnhancedHarmoniaApp replaces ``self.workspace`` with the notation
        # canvas. Descendant toolbars must be packed in the same container as
        # ``workspace_title``; using the canvas/viewport as the parent makes Tk
        # reject ``before=self.workspace_title`` on Windows.
        center = self.workspace_title.master
        controls = ttk.Frame(center)
        controls.pack(fill="x", before=self.workspace_title)

        ttk.Label(controls, text="Duration").pack(side="left", padx=(4,2))
        self.duration_var = tk.StringVar(value="1")
        ttk.Entry(controls, textvariable=self.duration_var, width=7).pack(side="left")
        ttk.Button(controls, text="Set", command=self._set_selected_duration).pack(side="left", padx=2)

        ttk.Label(controls, text="Lyrics").pack(side="left", padx=(8,2))
        self.lyrics_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.lyrics_var, width=16).pack(side="left")
        ttk.Button(controls, text="Apply", command=self._set_selected_lyrics).pack(side="left", padx=2)

        ttk.Label(controls, text="Harmony").pack(side="left", padx=(8,2))
        self.harmony_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.harmony_var, width=14).pack(side="left")
        ttk.Button(controls, text="Set", command=self._set_selected_harmony).pack(side="left", padx=2)

        ttk.Separator(controls, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Button(controls, text="+ Measure", command=self._add_measure_for_selection).pack(side="left", padx=2)
        ttk.Button(controls, text="− Measure", command=self._remove_measure_for_selection).pack(side="left", padx=2)

        # Later build layers historically use ``self.workspace.master`` as the
        # toolbar insertion point. Preserve that contract with a stable anchor
        # whose master is the shared center frame; the notation canvas remains
        # available as ``self.preview_canvas``.
        self.workspace = self.workspace_title

    def _selected_location(self):
        if self.selected_note is None:
            return None
        p, m, _n = self.selected_note
        return p, m

    def _set_selected_duration(self):
        editor = self._ensure_editor()
        if editor is None or self.selected_note is None:
            self.status_var.set("Select a note first")
            return
        try:
            duration = validate_duration(float(self.duration_var.get()))
            editor.change_duration(*self.selected_note, duration)
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid duration", str(exc), parent=self)
            return
        self._after_edit(f"Duration set to {duration:g} beats")

    def _set_selected_lyrics(self):
        editor = self._ensure_editor()
        if editor is None or self.selected_note is None:
            self.status_var.set("Select a note first")
            return
        editor.set_lyrics(*self.selected_note, self.lyrics_var.get().strip())
        self._after_edit("Lyrics updated")

    def _set_selected_harmony(self):
        editor = self._ensure_editor()
        location = self._selected_location()
        if editor is None or location is None:
            self.status_var.set("Select a note in the target measure first")
            return
        try:
            edit = parse_harmony_symbol(self.harmony_var.get())
        except ValueError as exc:
            messagebox.showerror("Invalid harmony", str(exc), parent=self)
            return
        if edit is None:
            self.status_var.set("Enter a harmony symbol, for example Cmaj7 or F#m7/C#")
            return
        p, m = location
        editor.set_harmony(p, m, 0, edit.to_harmony())
        self._after_edit(f"Harmony set to {edit.symbol}")

    def _add_measure_for_selection(self):
        editor = self._ensure_editor()
        if editor is None or self.controller.score is None or not self.controller.score.parts:
            self.status_var.set("Load a score first")
            return
        p = self.selected_note[0] if self.selected_note is not None else 0
        editor.add_measure(p)
        self.selected_note = None
        self._after_edit("Measure added")

    def _remove_measure_for_selection(self):
        editor = self._ensure_editor()
        location = self._selected_location()
        if editor is None or location is None:
            self.status_var.set("Select a note in the measure to remove")
            return
        p, m = location
        part = self.controller.score.parts[p]
        if len(part.measures) <= 1:
            messagebox.showwarning("Measure required", "A part must keep at least one measure.", parent=self)
            return
        editor.remove_measure(p, m)
        self.selected_note = None
        self._after_edit("Measure removed")

def main():
    from .logging_setup import configure_logging
    configure_logging()
    app = RichEditingHarmoniaApp()
    app.mainloop()

if __name__ == "__main__":
    main()
