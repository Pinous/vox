from pathlib import Path
from typing import Protocol

from vox.models.speaker_turn import SpeakerTurn


class Diarizer(Protocol):
    def diarize(
        self,
        audio_path: Path,
        num_speakers: int | None,
    ) -> tuple[SpeakerTurn, ...]: ...
