from pathlib import Path

from vox.models.transcription_result import TranscriptionResult


class FakeFileWriter:
    def __init__(self):
        self.srt_written: list[tuple[TranscriptionResult, Path]] = []
        self.txt_written: list[tuple[TranscriptionResult, Path]] = []
        self.json_written: list[tuple[TranscriptionResult, Path]] = []

    def write_srt(self, result: TranscriptionResult, path: Path) -> None:
        self.srt_written.append((result, path))

    def write_txt(self, result: TranscriptionResult, path: Path) -> None:
        self.txt_written.append((result, path))

    def write_json(self, result: TranscriptionResult, path: Path) -> None:
        self.json_written.append((result, path))
