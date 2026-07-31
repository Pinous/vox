from __future__ import annotations

import pytest

from tests.fakes.fake_audio_cleaner import FakeAudioCleaner
from tests.fakes.fake_diarizer import FakeDiarizer
from tests.fakes.fake_downloader import FakeDownloader
from tests.fakes.fake_file_writer import FakeFileWriter
from tests.fakes.fake_progress import FakeProgressReporter
from tests.fakes.fake_speaker_identifier import FakeSpeakerIdentifier
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
        self.diarizer = FakeDiarizer()
        self.speaker_identifier = FakeSpeakerIdentifier()
        self.use_case = TranscribeUseCase(
            downloader=self.downloader,
            audio_cleaner=self.audio_cleaner,
            transcriber=self.transcriber,
            file_writer=self.file_writer,
            progress=self.progress,
            diarizer=self.diarizer,
            speaker_identifier=self.speaker_identifier,
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
            "diarize": False,
            "identify": False,
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


class TestExecuteWhenDiarizeThenAssignsSpeakers:
    def test_execute_when_diarize_disabled_then_diarizer_not_called(self):
        fix = TranscribeFixture()

        fix.execute(diarize=False)

        assert fix.diarizer.diarize_called_with is None

    def test_execute_when_diarize_then_calls_diarizer(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        assert fix.diarizer.diarize_called_with is not None

    def test_execute_when_diarize_then_diarizes_same_file_as_transcribed(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        transcribed_path = fix.transcriber.transcribe_called_with[0]
        diarized_path = fix.diarizer.diarize_called_with[0]
        assert diarized_path == transcribed_path

    def test_execute_when_diarize_then_written_segments_carry_speaker(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        written_result = fix.file_writer.json_written[0][0]
        assert written_result.segments[0].speaker == "SPEAKER_00"

    def test_execute_when_diarize_disabled_then_segments_have_no_speaker(self):
        fix = TranscribeFixture()

        fix.execute(diarize=False)

        written_result = fix.file_writer.json_written[0][0]
        assert written_result.segments[0].speaker is None

    def test_execute_when_diarize_then_passes_num_speakers(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True, num_speakers=3)

        assert fix.diarizer.diarize_called_with[1] == 3


class TestExecuteWhenDiarizeThenPreservesAudioTimeline:
    def test_execute_when_diarize_then_silence_removal_disabled(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        config = fix.audio_cleaner.clean_called_with[1]
        assert config.remove_silence is False

    def test_execute_when_diarize_then_denoise_disabled(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        config = fix.audio_cleaner.clean_called_with[1]
        assert config.denoise is False

    def test_execute_when_diarize_then_still_mono_16k(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True)

        config = fix.audio_cleaner.clean_called_with[1]
        assert (config.sample_rate, config.channels) == (16000, 1)

    def test_execute_when_no_diarize_then_default_cleaning_kept(self):
        fix = TranscribeFixture()

        fix.execute(diarize=False)

        config = fix.audio_cleaner.clean_called_with[1]
        assert config.remove_silence is True
        assert config.denoise is True


class TestExecuteWhenIdentifyThenRenamesSpeakers:
    def test_execute_when_identify_then_labels_replaced_by_names(self):
        fix = TranscribeFixture()
        fix.speaker_identifier.mapping = {"SPEAKER_00": "Coco"}

        fix.execute(diarize=True, identify=True)

        written = fix.file_writer.json_written[0][0]
        assert written.segments[0].speaker == "Coco"

    def test_execute_when_identify_disabled_then_labels_kept(self):
        fix = TranscribeFixture()
        fix.speaker_identifier.mapping = {"SPEAKER_00": "Coco"}

        fix.execute(diarize=True, identify=False)

        written = fix.file_writer.json_written[0][0]
        assert written.segments[0].speaker == "SPEAKER_00"

    def test_execute_when_identify_without_diarize_then_no_identification(self):
        fix = TranscribeFixture()

        fix.execute(diarize=False, identify=True)

        assert fix.speaker_identifier.called_with is None

    def test_execute_when_identify_then_receives_diarized_turns(self):
        fix = TranscribeFixture()

        fix.execute(diarize=True, identify=True)

        _path, turns = fix.speaker_identifier.called_with
        assert turns[0].speaker == "SPEAKER_00"
