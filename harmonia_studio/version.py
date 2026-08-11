from dataclasses import dataclass

VERSION = "0.9.0"
BUILD = 46
CHANNEL = "preview"

@dataclass(frozen=True)
class VersionInfo:
    version: str = VERSION
    build: int = BUILD
    channel: str = CHANNEL

def get_version_info() -> VersionInfo:
    return VersionInfo()
