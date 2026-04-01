from dataclasses import dataclass

from vox.models.segment import Segment
from vox.models.word import Word


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    segments: tuple[Segment, ...]
    language: str
    words: tuple[Word, ...] | None = None
