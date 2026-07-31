from dataclasses import dataclass

from vox.models.exceptions import ValidationError


@dataclass(frozen=True)
class SpeakerTurn:
    start: float
    end: float
    speaker: str

    def __post_init__(self):
        if self.start < 0:
            raise ValidationError("start must be >= 0")
        if self.end <= self.start:
            raise ValidationError("end must be > start")
        if not self.speaker.strip():
            raise ValidationError("speaker must not be blank")
