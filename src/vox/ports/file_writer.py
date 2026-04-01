from pathlib import Path
from typing import Protocol

from vox.models.transcription_result import TranscriptionResult


class FileWriter(Protocol):
    def write_srt(self, result: TranscriptionResult, path: Path) -> None: ...

    def write_txt(self, result: TranscriptionResult, path: Path) -> None: ...

    def write_json(self, result: TranscriptionResult, path: Path) -> None: ...
