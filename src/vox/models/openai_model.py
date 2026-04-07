from enum import Enum

from vox.models.exceptions import ValidationError

_API_NAMES = {
    "GPT_4O_TRANSCRIBE": "gpt-4o-transcribe",
    "GPT_4O_MINI_TRANSCRIBE": "gpt-4o-mini-transcribe",
    "WHISPER_1": "whisper-1",
}

_SEGMENT_SUPPORT = {"WHISPER_1"}

_ALIAS_MAP = {
    "gpt-4o-transcribe": "GPT_4O_TRANSCRIBE",
    "gpt-4o-mini-transcribe": "GPT_4O_MINI_TRANSCRIBE",
    "whisper-1": "WHISPER_1",
}


class OpenAIModel(Enum):
    GPT_4O_TRANSCRIBE = "gpt-4o-transcribe"
    GPT_4O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
    WHISPER_1 = "whisper-1"

    @property
    def api_name(self) -> str:
        return _API_NAMES[self.name]

    @property
    def supports_segments(self) -> bool:
        return self.name in _SEGMENT_SUPPORT

    @classmethod
    def from_string(cls, name: str) -> "OpenAIModel":
        key = _ALIAS_MAP.get(name.lower())
        if key is None:
            raise ValidationError(f"Unknown OpenAI model: '{name}'")
        return cls[key]
