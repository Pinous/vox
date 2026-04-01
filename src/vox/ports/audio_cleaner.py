from pathlib import Path
from typing import Protocol

from vox.models.audio_config import AudioConfig


class AudioCleaner(Protocol):
    def clean(
        self,
        input_path: Path,
        config: AudioConfig,
        output_path: Path,
    ) -> Path: ...
