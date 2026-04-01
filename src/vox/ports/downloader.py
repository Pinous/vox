from pathlib import Path
from typing import Protocol

from vox.models.transcription_input import TranscriptionInput


class Downloader(Protocol):
    def download(
        self,
        source: TranscriptionInput,
        output_dir: Path,
    ) -> Path: ...
