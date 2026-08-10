from __future__ import annotations
import platform
from dataclasses import asdict
from .version import get_version_info
from .settings import app_data_dir, logs_dir, SCHEMA_VERSION

def diagnostics() -> dict:
    return {
        "version": asdict(get_version_info()),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "settingsSchema": SCHEMA_VERSION,
        "appDataPath": str(app_data_dir()),
        "logPath": str(logs_dir()),
    }
