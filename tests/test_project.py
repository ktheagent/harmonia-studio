import tempfile, unittest, json
from pathlib import Path
from harmonia_studio.project import ProjectService, ProjectDocument, PROJECT_EXTENSION, PROJECT_SCHEMA_VERSION

class ProjectTests(unittest.TestCase):
    def service(self, d):
        root=Path(d)
        return ProjectService(root/"recent.json", root/"recovery")

    def test_new_save_open_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.service(d)
            p=s.new("My Song")
            path=s.save(p, Path(d)/"song")
            self.assertEqual(path.suffix, PROJECT_EXTENSION)
            self.assertEqual(s.open(path).metadata.title, "My Song")

    def test_save_is_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.service(d); p=s.new()
            path=s.save(p, Path(d)/"x.harmonia")
            self.assertEqual(json.loads(path.read_text())["schemaVersion"], 2)

    def test_recent_projects(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.service(d); p=s.new()
            path=s.save(p, Path(d)/"x.harmonia")
            self.assertEqual(s.recent_projects()[0], str(path.resolve()))

    def test_autosave_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.service(d); p=s.new()
            a=s.autosave(p)
            self.assertTrue(a.exists())
            self.assertIn(a, s.recovery_candidates())

    def test_source_files_are_not_modified(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.musicxml"; source.write_text("ORIGINAL")
            s=self.service(d); p=s.new(); p.sourceFiles=[str(source)]
            s.save(p, Path(d)/"p.harmonia")
            self.assertEqual(source.read_text(), "ORIGINAL")

    def test_schema1_migrates_to_schema2(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"legacy.harmonia"
            p.write_text(json.dumps({"schemaVersion":1,"metadata":{"title":"Legacy"},"score":{},"sourceFiles":[]}))
            s=self.service(d); project=s.open(p)
            self.assertEqual(project.schemaVersion,PROJECT_SCHEMA_VERSION)
            self.assertEqual(project.history,{})
