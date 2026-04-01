from dataclasses import dataclass

from vox.models.exceptions import ValidationError


@dataclass(frozen=True)
class AudioConfig:
    remove_silence: bool = True
    denoise: bool = True
    normalize: bool = True
    sample_rate: int = 16000
    channels: int = 1

    def __post_init__(self):
        _validate_sample_rate(self.sample_rate)
        _validate_channels(self.channels)

    @classmethod
    def default(cls) -> "AudioConfig":
        return cls()


def _validate_sample_rate(sample_rate: int) -> None:
    if sample_rate <= 0:
        raise ValidationError(f"sample_rate must be > 0, got {sample_rate}")


def _validate_channels(channels: int) -> None:
    if channels not in (1, 2):
        raise ValidationError(f"channels must be 1 or 2, got {channels}")
