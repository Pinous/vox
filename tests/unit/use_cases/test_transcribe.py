from __future__ import annotations

import pytest

from tests.fakes.fake_audio_cleaner import FakeAudioCleaner
from tests.fakes.fake_downloader import FakeDownloader
from tests.fakes.fake_file_writer import FakeFileWriter
from tests.fakes.fake_progress import FakeProgressReporter
from tests.fakes.fake_transcriber import FakeTranscriber
from vox.models.exceptions import ValidationError
from vox.use_cases.transcribe import (
    TranscribeRequest,
    TranscribeResponse,
    TranscribeUseCase,
)


class TranscribeFixture:
    def __init__(self):
        self.downloader = FakeDownloader()
        self.audio_cleaner = FakeAudioCleaner()
        self.transcriber = FakeTranscriber()
        self.file_writer = FakeFileWriter()
        self.progress = FakeProgressReporter()
        self.use_case = TranscribeUseCase(
            downloader=self.downloader,
            audio_cleaner=self.audio_cleaner,
            transcriber=self.transcriber,
            file_writer=self.file_writer,
            progress=self.progress,
        )

    def execute(self, **overrides) -> TranscribeResponse:
        defaults = {
            "source": "test.mp3",
            "language": "auto",
            "model": "small",
            "output_dir": ".",
            "word_timestamps": False,
            "no_clean": False,
            "no_download": False,
            "dry_run": False,
        }
        defaults.update(overrides)
        request = TranscribeRequest(**defaults)
        return self.use_case.execute(request)


class TestExecuteWhenUrlInputThenDownloadsFirst:
    def test_execute_when_url_input_then_downloads_first(self):
        fix = TranscribeFixture()

        fix.execute(source="https://example.com/audio.mp3")

        assert fix.downloader.download_called_with is not None
        assert (
            fix.downloader.download_called_with.source
            == "https://example.com/audio.mp3"
        )


class TestExecuteWhenFileInputThenSkipsDownload:
    def test_execute_when_file_input_then_skips_download(self):
        fix = TranscribeFixture()

        fix.execute(source="test.mp3")

        assert fix.downloader.download_called_with is None


class TestExecuteWhenNoCleanThenSkipsAudioCleaning:
    def test_execute_when_no_clean_then_skips_audio_cleaning(self):
        fix = TranscribeFixture()

        fix.execute(no_clean=True)

        assert fix.audio_cleaner.clean_called_with is None


class TestExecuteWhenDefaultThenCleansAudio:
    def test_execute_when_default_then_cleans_audio(self):
        fix = TranscribeFixture()

        fix.execute()

        assert fix.audio_cleaner.clean_called_with is not None


class TestExecuteWhenValidThenTranscribes:
    def test_execute_when_valid_then_transcribes(self):
        fix = TranscribeFixture()

        result = fix.execute()

        assert fix.transcriber.transcribe_called_with is not None
        assert result.text == "Hello world"
        assert result.language == "en"


class TestExecuteWhenValidThenWritesAllOutputs:
    def test_execute_when_valid_then_writes_all_outputs(self):
        fix = TranscribeFixture()

        result = fix.execute(output_dir="/tmp/out")

        assert len(fix.file_writer.srt_written) == 1
        assert len(fix.file_writer.txt_written) == 1
        assert len(fix.file_writer.json_written) == 1
        assert result.srt_path.endswith(".srt")
        assert result.txt_path.endswith(".txt")
        assert result.json_path.endswith(".json")


class TestExecuteWhenDryRunThenDoesNotTranscribe:
    def test_execute_when_dry_run_then_does_not_transcribe(self):
        fix = TranscribeFixture()

        result = fix.execute(dry_run=True)

        assert fix.transcriber.transcribe_called_with is None
        assert fix.file_writer.srt_written == []
        assert "Execution plan:" in result.text


class TestExecuteWhenDryRunWithUrlThenShowsDownloadStep:
    def test_execute_when_dry_run_with_url_then_shows_download_step(self):
        fix = TranscribeFixture()

        result = fix.execute(
            source="https://youtube.com/watch?v=abc",
            dry_run=True,
        )

        assert "Download via yt-dlp" in result.text


class TestExecuteWhenDryRunNoCleanThenSkipsCleanStep:
    def test_execute_when_dry_run_no_clean_then_skips_clean_step(self):
        fix = TranscribeFixture()

        result = fix.execute(dry_run=True, no_clean=True)

        assert "Clean audio" not in result.text


class TestExecuteWhenWordTimestampsThenPassesToTranscriber:
    def test_execute_when_word_timestamps_then_passes_to_transcriber(
        self,
    ):
        fix = TranscribeFixture()

        fix.execute(word_timestamps=True)

        assert fix.transcriber.transcribe_called_with is not None
        _audio_path, _model, _language, word_ts = fix.transcriber.transcribe_called_with
        assert word_ts is True


class TestExecuteWhenValidThenReportsProgress:
    def test_execute_when_valid_then_reports_progress(self):
        fix = TranscribeFixture()

        fix.execute()

        assert len(fix.progress.steps) > 0
        assert fix.progress.finished is True


class TestExecuteWhenNoDownloadAndUrlThenRaises:
    def test_execute_when_no_download_and_url_then_raises(self):
        fix = TranscribeFixture()

        with pytest.raises(ValidationError, match="--no-download"):
            fix.execute(
                source="https://example.com/audio.mp3",
                no_download=True,
            )


class TestExecuteWhenValidThenOutputFilenamesMatchSource:
    def test_execute_when_file_input_then_filenames_use_stem(self):
        fix = TranscribeFixture()

        result = fix.execute(source="test.mp3", output_dir="/tmp/out")

        assert "test.srt" in result.srt_path
        assert "test.txt" in result.txt_path
        assert "test.json" in result.json_path

    def test_execute_when_url_input_then_filenames_use_vox_prefix(self):
        fix = TranscribeFixture()

        result = fix.execute(
            source="https://example.com/audio.mp3",
            output_dir="/tmp/out",
        )

        assert "vox_" in result.srt_path
        assert "vox_" in result.txt_path
        assert "vox_" in result.json_path
