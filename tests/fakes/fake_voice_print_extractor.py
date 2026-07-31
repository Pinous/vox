from pathlib import Path


class FakeVoicePrintExtractor:
    def __init__(
        self, embeddings: dict[tuple[float, float], tuple[float, ...]] | None = None
    ):
        self._embeddings = embeddings or {}
        self.extract_calls: list[tuple[Path, float, float]] = []

    def extract(
        self,
        audio_path: Path,
        start: float,
        end: float,
    ) -> tuple[float, ...]:
        self.extract_calls.append((audio_path, start, end))
        return self._embeddings.get((start, end), (1.0, 0.0))
