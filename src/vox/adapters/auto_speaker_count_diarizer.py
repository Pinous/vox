from pathlib import Path

from vox.models.clustering import cluster_embeddings
from vox.models.speaker_count import DEFAULT_MAX_SPEAKERS, estimate_speaker_count
from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_relabeling import merge_labels, relabel_turns
from vox.models.turn_selection import longest_turn_per_speaker
from vox.ports.diarizer import Diarizer
from vox.ports.voice_print_extractor import VoicePrintExtractor

OVERSEGMENTATION_THRESHOLD = 0.05


class AutoSpeakerCountDiarizer:
    def __init__(
        self,
        diarizer: Diarizer,
        extractor: VoicePrintExtractor,
        max_speakers: int = DEFAULT_MAX_SPEAKERS,
    ):
        self._diarizer = diarizer
        self._extractor = extractor
        self._max_speakers = max_speakers

    def diarize(
        self,
        audio_path: Path,
        num_speakers: int | None,
    ) -> tuple[SpeakerTurn, ...]:
        if num_speakers:
            return self._diarizer.diarize(audio_path, num_speakers)
        turns = self._diarizer.diarize(audio_path, None)
        longest = longest_turn_per_speaker(turns)
        if len(longest) < 2:
            return turns
        return self._merge_over_segmented(turns, longest, audio_path)

    def _merge_over_segmented(
        self,
        turns: tuple[SpeakerTurn, ...],
        longest: dict[str, SpeakerTurn],
        audio_path: Path,
    ) -> tuple[SpeakerTurn, ...]:
        labels = list(longest)
        embeddings = [
            self._extractor.extract(audio_path, longest[a].start, longest[a].end)
            for a in labels
        ]
        count = estimate_speaker_count(embeddings, self._max_speakers)
        groups = cluster_embeddings(embeddings, count)
        return relabel_turns(turns, merge_labels(labels, groups))
