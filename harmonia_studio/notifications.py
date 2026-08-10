from dataclasses import dataclass
from enum import Enum

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class Notification:
    type: NotificationType
    message: str
