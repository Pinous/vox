from dataclasses import dataclass
from pathlib import Path

from vox.models.exceptions import ValidationError
from vox.models.voice_print import VoicePrint
from vox.ports.voice_print_extractor import VoicePrintExtractor
from vox.ports.voice_print_store import VoicePrintStore

MIN_ENROLL_SECONDS = 2.0


@dataclass(frozen=True)
class EnrollSpeakerRequest:
    name: str
    audio_path: str
    start: float
    end: float


@dataclass(frozen=True)
class EnrollSpeakerResponse:
    name: str
    seconds_used: float


class EnrollSpeakerUseCase:
    def __init__(
        self,
        extractor: VoicePrintExtractor,
        store: VoicePrintStore,
    ):
        self._extractor = extractor
        self._store = store

    def execute(self, request: EnrollSpeakerRequest) -> EnrollSpeakerResponse:
        _validate_span(request.start, request.end)
        embedding = self._extractor.extract(
            Path(request.audio_path), request.start, request.end
        )
        self._store.save(VoicePrint(name=request.name, embedding=embedding))
        return EnrollSpeakerResponse(
            name=request.name,
            seconds_used=request.end - request.start,
        )


def _validate_span(start: float, end: float) -> None:
    if end <= start:
        raise ValidationError("end must be > start")
    if end - start < MIN_ENROLL_SECONDS:
        raise ValidationError(
            f"need at least {MIN_ENROLL_SECONDS} seconds of speech to enroll a voice"
        )
