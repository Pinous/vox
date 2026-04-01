from pathlib import Path

from vox.models.audio_config import AudioConfig


class FakeAudioCleaner:
    def __init__(self, result_path: Path = Path("/tmp/cleaned.wav")):
        self._result_path = result_path
        self.clean_called_with: tuple[Path, AudioConfig, Path] | None = None

    def clean(
        self,
        input_path: Path,
        config: AudioConfig,
        output_path: Path,
    ) -> Path:
        self.clean_called_with = (input_path, config, output_path)
        return self._result_path
