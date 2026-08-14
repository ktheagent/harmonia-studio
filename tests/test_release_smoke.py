import tempfile
import unittest
from pathlib import Path

from harmonia_studio.project import ProjectService


class ReleaseLifecycleSmokeTests(unittest.TestCase):
    def test_project_create_edit_save_reopen_autosave_cycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = ProjectService(root / "recent.json", root / "recovery")

            project = service.new("Build 51 Smoke")
            project.score = {
                "title": "Smoke Score",
                "parts": [{"id": "P1", "measures": [{"number": 1, "notes": [{"pitch": "C4"}]}]}],
            }
            project.history = {"entries": [{"action": "created"}]}

            path = service.save(project, root / "smoke-project")
            self.assertTrue(path.exists())

            reopened = service.open(path)
            self.assertEqual(reopened.metadata.title, "Build 51 Smoke")
            self.assertEqual(reopened.score["title"], "Smoke Score")

            reopened.score["title"] = "Edited Smoke Score"
            reopened.history["entries"].append({"action": "edited"})
            service.save(reopened)

            verified = service.open(path)
            self.assertEqual(verified.score["title"], "Edited Smoke Score")
            self.assertEqual(len(verified.history["entries"]), 2)

            recovery = service.autosave(verified)
            self.assertTrue(recovery.exists())
            self.assertIn(recovery, service.recovery_candidates())
            self.assertEqual(service.recent_projects()[0], str(path.resolve()))


if __name__ == "__main__":
    unittest.main()
