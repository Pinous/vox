from typing import Protocol

from vox.models.whisper_model import WhisperModel


class ModelManager(Protocol):
    def ensure_model(self, model: WhisperModel) -> str: ...

    def is_cached(self, model: WhisperModel) -> bool: ...
