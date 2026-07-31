from pathlib import Path

from vox.models.speaker_turn import SpeakerTurn


class FakeDiarizer:
    def __init__(self, turns: tuple[SpeakerTurn, ...] | None = None):
        self._turns = turns if turns is not None else _default_turns()
        self.diarize_called_with: tuple | None = None

    def diarize(
        self,
        audio_path: Path,
        num_speakers: int | None,
    ) -> tuple[SpeakerTurn, ...]:
        self.diarize_called_with = (audio_path, num_speakers)
        return self._turns


def _default_turns() -> tuple[SpeakerTurn, ...]:
    return (SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),)
