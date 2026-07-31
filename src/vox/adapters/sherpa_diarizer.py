from pathlib import Path

from vox.adapters.audio_decoding import decode_to_mono_16k
from vox.adapters.cpu_threads import default_num_threads
from vox.adapters.diarization_models import (
    EMBEDDING_FILE,
    EMBEDDING_REPO,
    SEGMENTATION_FILE,
    SEGMENTATION_REPO,
    ensure_model,
    import_sherpa,
)
from vox.models.exceptions import DiarizationError
from vox.models.speaker_turn import SpeakerTurn

_AUTO_CLUSTERS = -1


class SherpaDiarizer:
    def __init__(
        self,
        num_threads: int | None = None,
        clustering_threshold: float = 0.5,
    ):
        self._num_threads = num_threads or default_num_threads()
        self._clustering_threshold = clustering_threshold

    def diarize(
        self,
        audio_path: Path,
        num_speakers: int | None,
    ) -> tuple[SpeakerTurn, ...]:
        samples = decode_to_mono_16k(audio_path)
        pipeline = self._build_pipeline(num_speakers)
        try:
            result = pipeline.process(samples)
        except Exception as e:
            raise DiarizationError(str(e)) from e
        return _to_turns(result.sort_by_start_time())

    def _build_pipeline(self, num_speakers: int | None):
        sherpa_onnx = import_sherpa()
        config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
            segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
                pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(
                    model=ensure_model(SEGMENTATION_REPO, SEGMENTATION_FILE),
                ),
                num_threads=self._num_threads,
            ),
            embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(
                model=ensure_model(EMBEDDING_REPO, EMBEDDING_FILE),
                num_threads=self._num_threads,
            ),
            clustering=sherpa_onnx.FastClusteringConfig(
                num_clusters=num_speakers or _AUTO_CLUSTERS,
                threshold=self._clustering_threshold,
            ),
        )
        return sherpa_onnx.OfflineSpeakerDiarization(config)


def _to_turns(raw_segments) -> tuple[SpeakerTurn, ...]:
    return tuple(
        SpeakerTurn(
            start=s.start,
            end=s.end,
            speaker=_speaker_label(s.speaker),
        )
        for s in raw_segments
        if s.end > s.start
    )


def _speaker_label(speaker: int) -> str:
    return f"SPEAKER_{int(speaker):02d}"
