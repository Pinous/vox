from pathlib import Path

from vox.models.speaker_turn import SpeakerTurn


class FakeSpeakerIdentifier:
    def __init__(self, mapping: dict[str, str] | None = None):
        self.mapping = mapping or {}
        self.called_with: tuple[Path, tuple[SpeakerTurn, ...]] | None = None

    def execute(
        self,
        audio_path: Path,
        turns: tuple[SpeakerTurn, ...],
    ) -> dict[str, str]:
        self.called_with = (audio_path, turns)
        return self.mapping
