from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class ErrorCategory(str, Enum):
    FILE_SYSTEM = "FileSystem"
    CONFIGURATION = "Configuration"
    IMPORT = "Import"
    EXPORT = "Export"
    AUDIO = "Audio"
    NOTATION = "Notation"
    ANALYSIS = "Analysis"
    HARMONIZATION = "Harmonization"
    NETWORK = "Network"
    AI = "AI"
    INTERNAL = "Internal"

@dataclass
class AppError(Exception):
    code: str
    category: ErrorCategory
    message: str
    technical_details: str = ""
    recoverable: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
