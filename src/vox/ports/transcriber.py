from pathlib import Path
from typing import Protocol

from vox.models.transcription_result import TranscriptionResult


class Transcriber(Protocol):
    def transcribe(
        self,
        audio_path: Path,
        model: str,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult: ...
