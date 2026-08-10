from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    type: str
    state: JobState = JobState.QUEUED
    progress: float = 0.0
    message: str = ""
    cancellable: bool = True
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())
