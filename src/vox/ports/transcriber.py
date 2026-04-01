from pathlib import Path
from typing import Protocol

from vox.models.transcription_result import TranscriptionResult
from vox.models.whisper_model import WhisperModel


class Transcriber(Protocol):
    def transcribe(
        self,
        audio_path: Path,
        model: WhisperModel,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult: ...
