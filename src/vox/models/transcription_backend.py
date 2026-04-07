from enum import Enum

from vox.models.exceptions import ValidationError


class TranscriptionBackend(Enum):
    LOCAL = "local"
    OPENAI = "openai"

    @classmethod
    def from_string(cls, name: str) -> "TranscriptionBackend":
        try:
            return cls(name.lower())
        except ValueError:
            raise ValidationError(f"Unknown backend: '{name}'") from None
