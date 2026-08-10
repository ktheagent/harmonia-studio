from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json, os
from .settings import app_data_dir, SettingsService

PROJECT_SCHEMA_VERSION = 2
PROJECT_EXTENSION = ".harmonia"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class ProjectMetadata:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = "Untitled Project"
    composer: str = ""
    arranger: str = ""
    createdAt: str = field(default_factory=_now)
    modifiedAt: str = field(default_factory=_now)

@dataclass
class ProjectDocument:
    schemaVersion: int = PROJECT_SCHEMA_VERSION
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    score: dict = field(default_factory=dict)
    sourceFiles: list[str] = field(default_factory=list)
    history: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "metadata": asdict(self.metadata),
            "score": self.score,
            "sourceFiles": list(self.sourceFiles),
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectDocument":
        incoming=int(data.get("schemaVersion", 0))
        if incoming not in {1, PROJECT_SCHEMA_VERSION}:
            raise ValueError(f"Unsupported project schema: {data.get('schemaVersion')}")
        meta = ProjectMetadata(**data.get("metadata", {}))
        # Schema v1 -> v2 migration adds empty project history without touching score/source data.
        return cls(
            schemaVersion=PROJECT_SCHEMA_VERSION,
            metadata=meta,
            score=dict(data.get("score") or {}),
            sourceFiles=[str(x) for x in data.get("sourceFiles", [])],
            history=dict(data.get("history") or {}),
        )

class ProjectService:
    def __init__(self, recent_path: Path | None = None, recovery_dir: Path | None = None):
        self.recent_path = recent_path or app_data_dir() / "recent-projects.json"
        self.recovery_dir = recovery_dir or app_data_dir() / "recovery"
        self.current_path: Path | None = None
        self.current: ProjectDocument | None = None

    def new(self, title: str = "Untitled Project") -> ProjectDocument:
        self.current_path = None
        self.current = ProjectDocument(metadata=ProjectMetadata(title=title))
        return self.current

    def open(self, path: str | Path) -> ProjectDocument:
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        project = ProjectDocument.from_dict(data)
        self.current, self.current_path = project, p
        self._remember(p)
        return project

    def save(self, project: ProjectDocument | None = None, path: str | Path | None = None) -> Path:
        project = project or self.current
        if project is None:
            raise ValueError("No project to save")
        p = Path(path) if path else self.current_path
        if p is None:
            raise ValueError("A path is required for the first save")
        if p.suffix.lower() != PROJECT_EXTENSION:
            p = p.with_suffix(PROJECT_EXTENSION)
        p.parent.mkdir(parents=True, exist_ok=True)
        project.metadata.modifiedAt = _now()
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        os.replace(tmp, p)
        self.current, self.current_path = project, p
        self._remember(p)
        return p

    def autosave(self, project: ProjectDocument | None = None) -> Path:
        project = project or self.current
        if project is None:
            raise ValueError("No project to autosave")
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        path = self.recovery_dir / f"{project.metadata.id}.autosave{PROJECT_EXTENSION}"
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        os.replace(tmp, path)
        return path

    def recovery_candidates(self) -> list[Path]:
        if not self.recovery_dir.exists():
            return []
        return sorted(self.recovery_dir.glob(f"*.autosave{PROJECT_EXTENSION}"), key=lambda p: p.stat().st_mtime, reverse=True)

    def recent_projects(self, limit: int = 10) -> list[str]:
        if not self.recent_path.exists():
            return []
        try:
            items = json.loads(self.recent_path.read_text(encoding="utf-8"))
            return [x for x in items if Path(x).exists()][:limit]
        except Exception:
            return []

    def _remember(self, p: Path) -> None:
        self.recent_path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.recent_projects(limit=100)
        s = str(p.resolve())
        items = [s] + [x for x in existing if x != s]
        tmp = self.recent_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(items[:50], indent=2), encoding="utf-8")
        os.replace(tmp, self.recent_path)
