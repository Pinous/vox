from pathlib import Path

from vox.models.speaker_count import DEFAULT_MAX_SPEAKERS, estimate_speaker_count
from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_sampling import longest_turns
from vox.ports.diarizer import Diarizer
from vox.ports.voice_print_extractor import VoicePrintExtractor

OVERSEGMENTATION_THRESHOLD = 0.05
SAMPLE_SIZE = 24


class AutoSpeakerCountDiarizer:
    def __init__(
        self,
        diarizer: Diarizer,
        extractor: VoicePrintExtractor,
        max_speakers: int = DEFAULT_MAX_SPEAKERS,
        sample_size: int = SAMPLE_SIZE,
    ):
        self._diarizer = diarizer
        self._extractor = extractor
        self._max_speakers = max_speakers
        self._sample_size = sample_size

    def diarize(
        self,
        audio_path: Path,
        num_speakers: int | None,
    ) -> tuple[SpeakerTurn, ...]:
        if num_speakers:
            return self._diarizer.diarize(audio_path, num_speakers)
        probe = self._diarizer.diarize(audio_path, None)
        sample = longest_turns(probe, self._sample_size)
        if len(sample) < 2:
            return probe
        count = self._estimate_count(audio_path, sample)
        return self._diarizer.diarize(audio_path, count)

    def _estimate_count(
        self,
        audio_path: Path,
        sample: tuple[SpeakerTurn, ...],
    ) -> int:
        embeddings = [
            self._extractor.extract(audio_path, t.start, t.end) for t in sample
        ]
        return estimate_speaker_count(embeddings, self._max_speakers)
