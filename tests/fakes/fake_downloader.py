from pathlib import Path

from vox.models.transcription_input import TranscriptionInput


class FakeDownloader:
    def __init__(self, result_path: Path = Path("/tmp/downloaded.wav")):
        self._result_path = result_path
        self.download_called_with: TranscriptionInput | None = None

    def download(
        self,
        source: TranscriptionInput,
        output_dir: Path,
    ) -> Path:
        self.download_called_with = source
        return self._result_path
