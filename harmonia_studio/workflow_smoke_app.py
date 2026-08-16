from __future__ import annotations

import os
import tempfile
import traceback
from pathlib import Path

from .editor import ScoreEditor
from .menu_safe_app import MenuSafeHarmoniaApp
from .project import ProjectService
from .score import Measure, Note, Part, Pitch, Score


def build_workflow_smoke_score() -> Score:
    return Score(
        title="Build 55 Workflow Smoke",
        parts=[
            Part(
                "P1",
                "Piano",
                measures=[
                    Measure(
                        1,
                        notes=[
                            Note(Pitch("C", 4), duration=1.0, velocity=80),
                            Note(Pitch("E", 4), duration=1.0, velocity=76),
                        ],
                    )
                ],
            )
        ],
    )


def _write_report(text: str) -> None:
    report = os.environ.get("HARMONIA_WORKFLOW_REPORT", "").strip()
    if not report:
        return
    path = Path(report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


class WorkflowSmokeHarmoniaApp(MenuSafeHarmoniaApp):
    """Packaged-GUI workflow validation used only when explicitly enabled by CI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.environ.get("HARMONIA_WORKFLOW_SMOKE", "").strip() == "1":
            self.after_idle(self._run_workflow_smoke)

    def _run_workflow_smoke(self) -> None:
        try:
            with tempfile.TemporaryDirectory(prefix="harmonia-workflow-smoke-") as directory:
                root = Path(directory)
                self.projects = ProjectService(root / "recent.json", root / "recovery")
                self.projects.new("Build 55 Workflow Smoke")

                score = build_workflow_smoke_score()
                self.controller.set_score(score)
                self._sync_project_score()
                self._refresh_workspace()
                self.update_idletasks()

                editor = ScoreEditor(self.controller.require_score())
                editor.move_pitch(0, 0, 0, 2)
                editor.change_duration(0, 0, 0, 0.5)
                editor.set_lyrics(0, 0, 0, "smoke")
                edited = self.controller.require_score()
                if edited.parts[0].measures[0].notes[0].pitch.midi() != 62:
                    raise AssertionError("GUI workflow edit did not transpose C4 to D4")
                if edited.parts[0].measures[0].notes[0].duration != 0.5:
                    raise AssertionError("GUI workflow duration edit was not preserved")
                self._sync_project_score()
                self._refresh_workspace()
                self.update_idletasks()

                project_path = self.projects.save(path=root / "build55-workflow")
                self.projects.open(project_path)
                self._load_project_score()
                reopened = self.controller.require_score()
                if reopened.parts[0].measures[0].notes[0].pitch.midi() != 62:
                    raise AssertionError("Saved project did not preserve edited pitch")
                if not reopened.parts[0].measures[0].notes[0].lyrics:
                    raise AssertionError("Saved project did not preserve lyrics")
                self._refresh_workspace()
                self.update_idletasks()

                export_path = self.controller.export_file(root / "build55-workflow.musicxml")
                if not export_path.exists() or export_path.stat().st_size <= 0:
                    raise AssertionError("MusicXML export was not created")
                outcome = self.controller.import_file(export_path)
                if outcome.source_kind != "musicxml":
                    raise AssertionError("MusicXML re-import did not use the expected importer")
                if not outcome.score.parts:
                    raise AssertionError("MusicXML re-import produced no parts")
                self._refresh_workspace()
                self.update_idletasks()

                _write_report(
                    "OK\n"
                    "Packaged GUI workflow smoke completed successfully.\n"
                    f"Project: {project_path.name}\n"
                    f"Export: {export_path.name}"
                )
        except Exception:
            _write_report("WORKFLOW ERROR\n" + traceback.format_exc())
            raise
        finally:
            self.after_idle(self.destroy)
