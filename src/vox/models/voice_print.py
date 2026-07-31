from dataclasses import dataclass

from vox.models.exceptions import ValidationError


@dataclass(frozen=True)
class VoicePrint:
    name: str
    embedding: tuple[float, ...]

    def __post_init__(self):
        if not self.name.strip():
            raise ValidationError("name must not be blank")
        if not self.embedding:
            raise ValidationError("embedding must not be empty")
