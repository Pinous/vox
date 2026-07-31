from pathlib import Path

from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_selection import longest_turn_per_speaker
from vox.models.voice_matching import match_speakers
from vox.ports.voice_print_extractor import VoicePrintExtractor
from vox.ports.voice_print_store import VoicePrintStore

DEFAULT_MATCH_THRESHOLD = 0.8


class IdentifySpeakersUseCase:
    def __init__(
        self,
        extractor: VoicePrintExtractor,
        store: VoicePrintStore,
        threshold: float = DEFAULT_MATCH_THRESHOLD,
    ):
        self._extractor = extractor
        self._store = store
        self._threshold = threshold

    def execute(
        self,
        audio_path: Path,
        turns: tuple[SpeakerTurn, ...],
    ) -> dict[str, str]:
        prints = self._store.load_all()
        if not prints:
            return {}
        embeddings = self._embed_each_speaker(audio_path, turns)
        return match_speakers(embeddings, prints, self._threshold)

    def _embed_each_speaker(
        self,
        audio_path: Path,
        turns: tuple[SpeakerTurn, ...],
    ) -> dict[str, tuple[float, ...]]:
        return {
            label: self._extractor.extract(audio_path, turn.start, turn.end)
            for label, turn in longest_turn_per_speaker(turns).items()
        }
