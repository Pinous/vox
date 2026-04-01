from dataclasses import dataclass

from vox.models.exceptions import ValidationError


@dataclass(frozen=True)
class Word:
    start: float
    end: float
    word: str
    probability: float

    def __post_init__(self):
        if self.start < 0:
            raise ValidationError("start must be >= 0")
        if self.end <= self.start:
            raise ValidationError("end must be > start")
        if not 0 <= self.probability <= 1:
            raise ValidationError("probability must be between 0 and 1")
