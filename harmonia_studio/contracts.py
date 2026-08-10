"""Future engine contracts. Feature 001 defines interfaces only."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ScoreImporter(ABC):
    @abstractmethod
    def can_import(self, path: str) -> bool: ...
    @abstractmethod
    def import_score(self, path: str, options: dict | None = None) -> Any: ...

class ScoreExporter(ABC):
    @abstractmethod
    def export_score(self, score: Any, path: str, options: dict | None = None) -> None: ...

class MusicAnalyzer(ABC):
    @abstractmethod
    def analyze(self, score: Any) -> Any: ...

class HarmonyGenerator(ABC):
    @abstractmethod
    def generate(self, score: Any, options: dict | None = None) -> Any: ...

class HarmonyValidator(ABC):
    @abstractmethod
    def validate(self, score: Any, profile: str = "default") -> Any: ...

class PlaybackEngine(ABC):
    @abstractmethod
    def play(self, score: Any) -> None: ...

class NotationRenderer(ABC):
    @abstractmethod
    def render(self, score: Any) -> Any: ...

class TranscriptionEngine(ABC):
    @abstractmethod
    def transcribe(self, path: str) -> Any: ...
