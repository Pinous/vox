from enum import Enum

from vox.models.exceptions import ValidationError

_ALIAS_MAP = {
    "large-v3": "LARGE_V3",
}


class WhisperModel(Enum):
    TINY = "mlx-community/whisper-tiny-mlx"
    BASE = "mlx-community/whisper-base-mlx"
    SMALL = "mlx-community/whisper-small-mlx"
    MEDIUM = "mlx-community/whisper-medium-mlx"
    LARGE_V3 = "mlx-community/whisper-large-v3-mlx"

    @property
    def hf_repo(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, name: str) -> "WhisperModel":
        normalized = _normalize(name)
        return _resolve(cls, normalized)


def _normalize(name: str) -> str:
    return _ALIAS_MAP.get(name.lower(), name.upper())


def _resolve(cls: type[WhisperModel], key: str) -> WhisperModel:
    try:
        return cls[key]
    except KeyError:
        raise ValidationError(f"Unknown whisper model: '{key}'") from None
