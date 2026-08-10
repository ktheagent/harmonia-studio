from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from .settings import SettingsService
from .logging_setup import configure_logging
from .version import get_version_info
from .project import ProjectService
from .score import Score
from .controller import StudioController
from .harmony.styles import STYLE_REGISTRY
from .arrangement.templates import TEMPLATES


IMPORT_TYPES = [
    ("Supported music", "*.musicxml *.xml *.mxl *.mid *.midi *.pdf *.png *.jpg *.jpeg *.tif *.tiff *.wav *.mp3 *.flac *.aac *.m4a"),
    ("MusicXML", "*.musicxml *.xml *.mxl"),
    ("MIDI", "*.mid *.midi"),
    ("Scores / images", "*.pdf *.png *.jpg *.jpeg *.tif *.tiff"),
    ("Audio", "*.wav *.mp3 *.flac *.aac *.m4a"),
    ("All files", "*.*"),
]

EXPORT_TYPES = [
    ("MusicXML", "*.musicxml"),
    ("Compressed MusicXML", "*.mxl"),
    ("MIDI", "*.mid"),
    ("PDF score", "*.pdf"),
    ("WAV audio", "*.wav"),
    ("MP3 audio", "*.mp3"),
]


class HarmoniaApp(tk.Tk):
    def __init__(self, settings_service: SettingsService | None = None):
        super().__init__()
        self.title("Harmonia Studio")
        self.geometry("1440x900")
        self.minsize(1000, 650)
        self.settings_service = settings_service or SettingsService()
        self.settings = self.settings_service.load()
        self.projects = ProjectService()
        self.controller = StudioController()
        self._configure_style()
        self.protocol("WM_DELETE_WINDOW", self._shutdown)
        self._build_menu()
        self._build_shell()
        self._refresh_workspace()

    def _configure_style(self):
        style = ttk.Style(self)
        if self.settings.theme == "dark":
            self.configure(bg="#202225")
            style.configure("TFrame", background="#202225")
            style.configure("TLabel", background="#202225", foreground="#f3f3f3")
        elif self.settings.theme == "light":
            self.configure(bg="#f4f4f4")

    def _build_menu(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="New Project", command=self._new_project)
        filem.add_command(label="Open Project", command=self._open_project)
        filem.add_command(label="Recent Projects", command=self._show_recent)
        filem.add_separator()
        filem.add_command(label="Save", command=self._save_project)
        filem.add_command(label="Save As", command=lambda: self._save_project(save_as=True))
        filem.add_separator()
        filem.add_command(label="Import Music…", command=self._import_music)
        filem.add_command(label="Export…", command=self._export_music)
        filem.add_separator()
        filem.add_command(label="Exit", command=self._shutdown)
        menubar.add_cascade(label="File", menu=filem)

        edit = tk.Menu(menubar, tearoff=0)
        for label in ["Undo", "Redo", "Cut", "Copy", "Paste"]:
            edit.add_command(label=label, state="disabled")
        edit.add_separator()
        edit.add_command(label="Preferences", command=self._show_preferences)
        menubar.add_cascade(label="Edit", menu=edit)

        view = tk.Menu(menubar, tearoff=0)
        view.add_command(label="Refresh Workspace", command=self._refresh_workspace)
        menubar.add_cascade(label="View", menu=view)

        playback = tk.Menu(menubar, tearoff=0)
        playback.add_command(
            label="Playback Engine Status",
            command=lambda: messagebox.showinfo(
                "Playback",
                "The timed playback engine is implemented. This preview does not claim validated physical audio-device playback; use WAV/MP3 export for audible rendering.",
            ),
        )
        menubar.add_cascade(label="Playback", menu=playback)

        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Analyze", command=self._analyze)
        tools.add_command(label="Harmonize", command=self._harmonize)
        tools.add_command(label="Arrange", command=self._arrange)
        tools.add_command(
            label="Transcription",
            command=lambda: messagebox.showinfo(
                "Transcription",
                "Import WAV, MP3, FLAC, AAC or M4A to run melody, tempo and meter transcription.",
            ),
        )
        tools.add_command(label="Validate Harmony", command=self._validate_harmony)
        menubar.add_cascade(label="Tools", menu=tools)

        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="About Harmonia Studio", command=self._show_about)
        menubar.add_cascade(label="Help", menu=helpm)
        self.config(menu=menubar)

    def _build_shell(self):
        toolbar = ttk.Frame(self, padding=6)
        toolbar.pack(fill="x")
        buttons = [
            ("New", self._new_project),
            ("Open", self._open_project),
            ("Save", self._save_project),
            ("Analyze", self._analyze),
            ("Harmonize", self._harmonize),
            ("Export", self._export_music),
        ]
        for label, command in buttons:
            ttk.Button(toolbar, text=label, command=command).pack(side="left", padx=2)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, width=230, padding=8)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Project / Parts").pack(anchor="w")
        self.parts_list = tk.Listbox(left, width=28, height=30)
        self.parts_list.pack(fill="both", expand=True, pady=(8, 0))

        center = ttk.Frame(body, padding=20)
        center.pack(side="left", fill="both", expand=True)
        self.workspace_title = ttk.Label(center, text="Welcome to Harmonia Studio", font=("TkDefaultFont", 20, "bold"))
        self.workspace_title.pack(pady=(40, 10))
        self.workspace = tk.Text(center, wrap="word", height=30, state="disabled")
        self.workspace.pack(fill="both", expand=True)

        right = ttk.Frame(body, width=260, padding=8)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Inspector / Properties").pack(anchor="w")
        self.inspector = tk.Text(right, width=30, height=28, state="disabled")
        self.inspector.pack(fill="both", expand=True, pady=(8, 0))

        v = get_version_info()
        status = ttk.Frame(self, padding=(8, 4))
        status.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status, textvariable=self.status_var).pack(side="left")
        ttk.Label(status, text=f"Harmonia Studio {v.version} preview").pack(side="right")

    @staticmethod
    def _set_text(widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _sync_project_score(self):
        if self.projects.current is not None and self.controller.score is not None:
            self.projects.current.score = self.controller.score.to_dict()

    def _load_project_score(self):
        if self.projects.current is not None and self.projects.current.score:
            self.controller.set_score(Score.from_dict(self.projects.current.score))
        else:
            self.controller.score = None

    def _refresh_workspace(self):
        score = self.controller.score
        self.parts_list.delete(0, "end")
        if score is None:
            self.workspace_title.configure(text="Welcome to Harmonia Studio")
            self._set_text(
                self.workspace,
                "Create or open a project, then choose File → Import Music.\n\n"
                "Supported workflows in this preview include notation/MIDI import, PDF/image OMR, "
                "audio melody transcription, analysis, harmonization, arrangement, and export.",
            )
            self._set_text(self.inspector, "No score loaded.")
            return
        self.workspace_title.configure(text=score.title or "Untitled Score")
        total_measures = max((len(p.measures) for p in score.parts), default=0)
        total_notes = sum(1 for n in score.iter_notes() if n.pitch is not None)
        for part in score.parts:
            self.parts_list.insert("end", f"{part.name}  ({len(part.measures)} measures)")
        self._set_text(
            self.workspace,
            f"Score: {score.title}\nComposer: {score.composer or '—'}\n"
            f"Parts: {len(score.parts)}\nMeasures: {total_measures}\nNotes: {total_notes}\n\n"
            "Use Tools → Analyze for tonal/chord/quality analysis.\n"
            "Use Tools → Harmonize to create three candidates and select one.\n"
            "Use Tools → Arrange to distribute the score to an ensemble.\n"
            "Use File → Export for MusicXML, MIDI, PDF, WAV or MP3.",
        )
        metadata = "\n".join(f"{k}: {v}" for k, v in sorted(score.metadata.items())) or "No score metadata."
        self._set_text(self.inspector, metadata)

    def _new_project(self):
        title = simpledialog.askstring("New Project", "Project title:", initialvalue="Untitled Project", parent=self)
        if title is not None:
            project = self.projects.new(title or "Untitled Project")
            self.controller.score = None
            self.title(f"{project.metadata.title} — Harmonia Studio")
            self.status_var.set("New project created")
            self._refresh_workspace()

    def _open_project(self):
        path = filedialog.askopenfilename(title="Open Harmonia Project", filetypes=[("Harmonia Project", "*.harmonia")])
        if path:
            try:
                project = self.projects.open(path)
                self._load_project_score()
                self.title(f"{project.metadata.title} — Harmonia Studio")
                self.status_var.set(f"Opened {project.metadata.title}")
                self._refresh_workspace()
            except Exception as e:
                messagebox.showerror("Open Project", str(e))

    def _save_project(self, save_as=False):
        if self.projects.current is None:
            messagebox.showwarning("Save Project", "Create or open a project first.")
            return
        self._sync_project_score()
        path = None
        if save_as or self.projects.current_path is None:
            path = filedialog.asksaveasfilename(
                title="Save Harmonia Project",
                defaultextension=".harmonia",
                filetypes=[("Harmonia Project", "*.harmonia")],
            )
            if not path:
                return
        try:
            saved = self.projects.save(path=path)
            self.status_var.set(f"Saved {saved.name}")
        except Exception as e:
            messagebox.showerror("Save Project", str(e))

    def _import_music(self):
        path = filedialog.askopenfilename(title="Import Music", filetypes=IMPORT_TYPES)
        if not path:
            return
        try:
            self.status_var.set("Importing…")
            outcome = self.controller.import_file(path)
            if self.projects.current is None:
                self.projects.new(self.controller.score.title or "Imported Project")
            self.projects.current.sourceFiles.append(str(path))
            self._sync_project_score()
            self._refresh_workspace()
            self.status_var.set(f"Imported {outcome.source_kind}")
            if outcome.source_kind == "omr" and (outcome.confidence < 0.8 or outcome.warnings):
                messagebox.showwarning(
                    "OMR Verification Recommended",
                    f"Recognition confidence: {outcome.confidence:.0%}\n\n"
                    + ("\n".join(outcome.warnings[:5]) if outcome.warnings else "Review recognized notation before harmonizing."),
                )
            elif outcome.source_kind == "audio-transcription":
                messagebox.showinfo(
                    "Audio Transcription",
                    f"Melody transcription confidence: {outcome.confidence:.0%}\n"
                    f"Detected tempo: {outcome.details.get('bpm', 0):.1f} BPM\n"
                    f"Detected meter: {outcome.details.get('meter', '—')}",
                )
        except Exception as e:
            self.status_var.set("Import failed")
            messagebox.showerror("Import Music", str(e))

    def _export_music(self):
        if self.controller.score is None:
            messagebox.showwarning("Export", "Import or create a score first.")
            return
        path = filedialog.asksaveasfilename(title="Export", filetypes=EXPORT_TYPES, defaultextension=".musicxml")
        if not path:
            return
        try:
            out = self.controller.export_file(path)
            self.status_var.set(f"Exported {out.name}")
            messagebox.showinfo("Export Complete", f"Created:\n{out}")
        except Exception as e:
            self.status_var.set("Export failed")
            messagebox.showerror("Export", str(e))

    def _analyze(self):
        if self.controller.score is None:
            messagebox.showwarning("Analyze", "Import or open a score first.")
            return
        try:
            bundle = self.controller.analyze()
            key = bundle.tonality.global_key
            chord_names = [c.symbol for c in bundle.chords[:12]]
            messagebox.showinfo(
                "Music Analysis",
                f"Estimated key: {key.tonic} {key.mode} ({key.confidence:.0%} confidence)\n"
                f"Detected chords: {', '.join(chord_names) if chord_names else 'None'}\n"
                f"Quality score: {bundle.quality.metrics.overall:.1f}%\n"
                f"Phrase boundaries: {len(bundle.phrases.phrase_boundaries)}",
            )
            self.status_var.set("Analysis complete")
        except Exception as e:
            messagebox.showerror("Analyze", str(e))

    def _harmonize(self):
        if self.controller.score is None:
            messagebox.showwarning("Harmonize", "Import or open a score first.")
            return
        styles = ", ".join(STYLE_REGISTRY.keys())
        style = simpledialog.askstring("Harmonize", f"Style ({styles}):", initialvalue="hymn", parent=self)
        if not style:
            return
        style = style.strip().lower()
        if style not in STYLE_REGISTRY:
            messagebox.showerror("Harmonize", f"Unknown style: {style}")
            return
        try:
            source = self.controller.score
            _, candidates = self.controller.harmonize(style, 0)
            labels = "\n".join(f"{i+1}. {c.label} — {c.quality_score:.1f}%" for i, c in enumerate(candidates))
            choice = simpledialog.askinteger(
                "Choose Harmonization",
                f"{labels}\n\nChoose candidate 1–3:",
                minvalue=1, maxvalue=3, initialvalue=1, parent=self,
            )
            if choice is None:
                self.controller.score = source
                return
            self.controller.score = candidates[choice - 1].result.score
            self._sync_project_score()
            self._refresh_workspace()
            self.status_var.set(f"Harmonized: {style} / {candidates[choice-1].label}")
        except Exception as e:
            messagebox.showerror("Harmonize", str(e))

    def _arrange(self):
        if self.controller.score is None:
            messagebox.showwarning("Arrange", "Import or open a score first.")
            return
        names = ", ".join(TEMPLATES.keys())
        ensemble = simpledialog.askstring("Arrange", f"Ensemble ({names}):", initialvalue="piano_vocal", parent=self)
        if not ensemble:
            return
        ensemble = ensemble.strip().lower()
        if ensemble not in TEMPLATES:
            messagebox.showerror("Arrange", f"Unknown ensemble: {ensemble}")
            return
        try:
            self.controller.arrange(ensemble)
            self._sync_project_score()
            self._refresh_workspace()
            self.status_var.set(f"Arranged for {ensemble}")
        except Exception as e:
            messagebox.showerror("Arrange", str(e))

    def _validate_harmony(self):
        if self.controller.score is None:
            messagebox.showwarning("Validate", "Import or open a score first.")
            return
        try:
            q = self.controller.analyze().quality
            warnings = "\n".join(q.warnings[:10]) or "No voice-leading warnings detected."
            messagebox.showinfo(
                "Harmony Validation",
                f"Overall: {q.metrics.overall:.1f}%\n"
                f"Voice leading: {q.metrics.voice_leading:.1f}%\n"
                f"Range compliance: {q.metrics.range_compliance:.1f}%\n\n{warnings}",
            )
        except Exception as e:
            messagebox.showerror("Validate Harmony", str(e))

    def _show_recent(self):
        items = self.projects.recent_projects(self.settings.recentProjectLimit)
        messagebox.showinfo("Recent Projects", "\n".join(items) if items else "No recent projects.")

    def _show_about(self):
        v = get_version_info()
        messagebox.showinfo(
            "About Harmonia Studio",
            f"Harmonia Studio\n\nVersion {v.version}\nBuild {v.build}\nChannel {v.channel}\n\n"
            "AI-assisted music harmonization, arrangement and notation workstation.",
        )

    def _show_preferences(self):
        win = tk.Toplevel(self)
        win.title("Preferences")
        win.transient(self)
        win.grab_set()
        ttk.Label(win, text="Theme").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        var = tk.StringVar(value=self.settings.theme)
        combo = ttk.Combobox(win, textvariable=var, values=["system", "light", "dark"], state="readonly")
        combo.grid(row=0, column=1, padx=10, pady=10)

        def save():
            self.settings.theme = var.get()
            self.settings_service.save(self.settings)
            messagebox.showinfo("Harmonia Studio", "Settings saved. Restart to fully apply the theme.")
            win.destroy()

        ttk.Button(win, text="Save", command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def report_callback_exception(self, exc, val, tb):
        logging.getLogger("harmonia").exception("Unhandled UI error", exc_info=(exc, val, tb))
        messagebox.showerror(
            "Harmonia Studio",
            "Harmonia Studio encountered an unexpected problem. Technical details were written to the application log.",
        )

    def _shutdown(self):
        try:
            self._sync_project_score()
            self.settings_service.save(self.settings)
        finally:
            self.destroy()


def main():
    configure_logging()
    logging.getLogger("harmonia").info("Starting Harmonia Studio")
    app = HarmoniaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
