from pathlib import Path

from vox.models.segment import Segment
from vox.models.transcription_result import TranscriptionResult


class FakeTranscriber:
    def __init__(
        self,
        result: TranscriptionResult | None = None,
    ):
        self._result = result or _default_result()
        self.transcribe_called_with: tuple | None = None

    def transcribe(
        self,
        audio_path: Path,
        model: str,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult:
        self.transcribe_called_with = (
            audio_path,
            model,
            language,
            word_timestamps,
        )
        return self._result


def _default_result() -> TranscriptionResult:
    return TranscriptionResult(
        text="Hello world",
        segments=(Segment(start=0.0, end=1.0, text="Hello world"),),
        language="en",
    )
