import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harmonia_studio.workflow_smoke_app import _write_report, build_workflow_smoke_score


class WorkflowSmokeAppTests(unittest.TestCase):
    def test_workflow_score_has_editable_notes(self):
        score = build_workflow_smoke_score()
        self.assertEqual(score.title, "Build 55 Workflow Smoke")
        self.assertEqual(len(score.parts), 1)
        self.assertEqual(len(score.parts[0].measures), 1)
        self.assertEqual(len(score.parts[0].measures[0].notes), 2)

    def test_workflow_score_starts_on_middle_c(self):
        score = build_workflow_smoke_score()
        self.assertEqual(score.parts[0].measures[0].notes[0].pitch.midi(), 60)

    def test_report_writer_uses_explicit_ci_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflow.txt"
            with patch.dict(os.environ, {"HARMONIA_WORKFLOW_REPORT": str(path)}, clear=False):
                _write_report("OK\ncomplete")
            self.assertTrue(path.exists())
            self.assertTrue(path.read_text(encoding="utf-8").startswith("OK\n"))


if __name__ == "__main__":
    unittest.main()
