from pathlib import Path
from typing import Protocol


class VoicePrintExtractor(Protocol):
    def extract(
        self,
        audio_path: Path,
        start: float,
        end: float,
    ) -> tuple[float, ...]: ...
