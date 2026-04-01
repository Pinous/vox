from dataclasses import dataclass

from vox.models.exceptions import ValidationError


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str

    def __post_init__(self):
        if self.start < 0:
            raise ValidationError("start must be >= 0")
        if self.end <= self.start:
            raise ValidationError("end must be > start")
