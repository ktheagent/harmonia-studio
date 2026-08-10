from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import platform
import shutil
from typing import Literal

Theme = Literal["system", "light", "dark"]
SCHEMA_VERSION = 1

def app_data_dir() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif platform.system() == "Darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "HarmoniaStudio"

def logs_dir() -> Path:
    p = app_data_dir() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p

@dataclass
class AppSettings:
    schemaVersion: int = SCHEMA_VERSION
    theme: Theme = "system"
    language: str = "en"
    recentProjectLimit: int = 10
    reopenLastProject: bool = False
    autosaveEnabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        if int(data.get("schemaVersion", 0)) != SCHEMA_VERSION:
            raise ValueError("Unsupported settings schema")
        theme = data.get("theme", "system")
        if theme not in {"system", "light", "dark"}:
            raise ValueError("Invalid theme")
        return cls(
            schemaVersion=SCHEMA_VERSION,
            theme=theme,
            language=str(data.get("language", "en")),
            recentProjectLimit=max(1, min(50, int(data.get("recentProjectLimit", 10)))),
            reopenLastProject=bool(data.get("reopenLastProject", False)),
            autosaveEnabled=bool(data.get("autosaveEnabled", True)),
        )

class SettingsService:
    def __init__(self, path: Path | None = None):
        self.path = path or app_data_dir() / "settings.json"

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            return AppSettings.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception:
            corrupt = self.path.with_suffix(self.path.suffix + ".corrupt")
            try:
                shutil.copy2(self.path, corrupt)
            except Exception:
                pass
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
        os.replace(tmp, self.path)
