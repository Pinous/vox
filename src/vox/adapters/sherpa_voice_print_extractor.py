from pathlib import Path

from vox.adapters.audio_decoding import SAMPLE_RATE, decode_to_mono_16k, slice_samples
from vox.adapters.cpu_threads import default_num_threads
from vox.adapters.diarization_models import (
    EMBEDDING_FILE,
    EMBEDDING_REPO,
    ensure_model,
    import_sherpa,
)
from vox.models.exceptions import DiarizationError


class SherpaVoicePrintExtractor:
    def __init__(self, num_threads: int | None = None):
        self._num_threads = num_threads or default_num_threads()
        self._extractor = None

    def extract(
        self,
        audio_path: Path,
        start: float,
        end: float,
    ) -> tuple[float, ...]:
        samples = slice_samples(decode_to_mono_16k(audio_path), start, end)
        if len(samples) == 0:
            raise DiarizationError(f"no audio between {start}s and {end}s")
        extractor = self._ensure_extractor()
        stream = extractor.create_stream()
        stream.accept_waveform(SAMPLE_RATE, samples)
        stream.input_finished()
        return tuple(extractor.compute(stream))

    def _ensure_extractor(self):
        if self._extractor is None:
            sherpa_onnx = import_sherpa()
            self._extractor = sherpa_onnx.SpeakerEmbeddingExtractor(
                sherpa_onnx.SpeakerEmbeddingExtractorConfig(
                    model=ensure_model(EMBEDDING_REPO, EMBEDDING_FILE),
                    num_threads=self._num_threads,
                )
            )
        return self._extractor
