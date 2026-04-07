from tests.fakes.fake_audio_cleaner import FakeAudioCleaner
from tests.fakes.fake_channel_lister import FakeChannelLister
from tests.fakes.fake_downloader import FakeDownloader
from tests.fakes.fake_file_cleaner import FakeFileCleaner
from tests.fakes.fake_file_uploader import FakeFileUploader
from tests.fakes.fake_file_writer import FakeFileWriter
from tests.fakes.fake_metadata_writer import FakeMetadataWriter
from tests.fakes.fake_progress import FakeProgressReporter
from tests.fakes.fake_summarizer import FakeSummarizer
from tests.fakes.fake_transcriber import FakeTranscriber
from vox.models.channel_video import ChannelVideo
from vox.models.exceptions import DownloadError
from vox.use_cases.batch_transcribe import (
    BatchTranscribeRequest,
    BatchTranscribeUseCase,
)
from vox.use_cases.transcribe import TranscribeUseCase


def _video(video_id="v1", title="Scalping Nasdaq Live", date="20250315"):
    return ChannelVideo(
        video_id=video_id,
        title=title,
        url=f"https://www.youtube.com/watch?v={video_id}",
        upload_date=date,
        channel_name="XEILOSTRADING",
        duration_seconds=1320,
    )


def _two_videos():
    return (
        _video("v1", "Scalping Nasdaq Session 1", "20250315"),
        _video("v2", "Scalping Nasdaq Session 2", "20250420"),
    )


class Fixture:
    def __init__(self, videos=(), failing_transcriber=False):
        self.channel_lister = FakeChannelLister(videos=videos)
        self.downloader = FakeDownloader()
        self.audio_cleaner = FakeAudioCleaner()
        self.file_writer = FakeFileWriter()
        self.file_uploader = FakeFileUploader()
        self.file_cleaner = FakeFileCleaner()
        self.progress = FakeProgressReporter()
        self.summarizer = FakeSummarizer()
        self.metadata_writer = FakeMetadataWriter()

        if failing_transcriber:
            self.transcriber = _FailingTranscriber()
        else:
            self.transcriber = FakeTranscriber()

        self.transcribe_use_case = TranscribeUseCase(
            downloader=self.downloader,
            audio_cleaner=self.audio_cleaner,
            transcriber=self.transcriber,
            file_writer=self.file_writer,
            progress=self.progress,
        )
        self.use_case = BatchTranscribeUseCase(
            channel_lister=self.channel_lister,
            transcribe=self.transcribe_use_case,
            file_uploader=self.file_uploader,
            file_cleaner=self.file_cleaner,
            progress=self.progress,
            summarizer=self.summarizer,
            metadata_writer=self.metadata_writer,
        )


class _FailingTranscriber:
    def transcribe(self, audio_path, model, language, word_timestamps):
        raise DownloadError("Network error")


def _request(**overrides):
    defaults = {
        "channel_url": "https://www.youtube.com/@XEILOSTRADING/search?query=scalping",
        "years": (2025, 2026),
        "output_dir": "/tmp/vox_test",
    }
    defaults.update(overrides)
    return BatchTranscribeRequest(**defaults)


class TestBatchTranscribeUseCase:
    def test_execute_when_channel_has_videos_then_transcribes_each(self):
        fixture = Fixture(videos=_two_videos())

        result = fixture.use_case.execute(_request())

        assert result.total == 2
        assert result.succeeded == 2
        assert result.failed == 0

    def test_execute_when_no_videos_found_then_returns_empty(self):
        fixture = Fixture(videos=())

        result = fixture.use_case.execute(_request())

        assert result.total == 0
        assert result.succeeded == 0
        assert result.items == ()

    def test_execute_when_dry_run_then_lists_without_transcribing(self):
        fixture = Fixture(videos=_two_videos())

        result = fixture.use_case.execute(_request(dry_run=True))

        assert result.total == 2
        assert result.succeeded == 0
        assert fixture.downloader.download_called_with is None

    def test_execute_when_one_video_fails_then_continues(self):
        fixture = Fixture(videos=_two_videos(), failing_transcriber=True)

        result = fixture.use_case.execute(_request())

        assert result.total == 2
        assert result.failed == 2

    def test_execute_when_upload_enabled_then_uploads_outputs(self):
        fixture = Fixture(videos=(_video(),))

        result = fixture.use_case.execute(
            _request(upload=True, remote_name="gdrive", remote_folder="transcripts")
        )

        assert result.succeeded == 1
        assert len(fixture.file_uploader.uploads) >= 3

    def test_execute_when_upload_disabled_then_skips_upload(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request(upload=False))

        assert fixture.file_uploader.uploads == []

    def test_execute_when_cleanup_disabled_then_keeps_files(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request(cleanup=False))

        assert fixture.file_cleaner.deleted == []

    def test_execute_when_upload_then_folder_has_channel_and_video(self):
        fixture = Fixture(videos=(_video(title="Ma Video"),))

        fixture.use_case.execute(
            _request(upload=True, remote_name="gdrive", remote_folder="root")
        )

        video_uploads = [
            folder
            for _, folder in fixture.file_uploader.uploads
            if "Ma Video" in folder
        ]
        assert len(video_uploads) >= 3
        assert all("XEILOSTRADING" in f for f in video_uploads)

    def test_execute_passes_correct_years_to_lister(self):
        fixture = Fixture(videos=())

        fixture.use_case.execute(_request(years=(2025, 2026)))

        _url, date_range = fixture.channel_lister.list_called_with
        assert date_range.after == "20250101"
        assert date_range.before == "20261231"

    def test_execute_when_success_then_calls_summarizer(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request())

        assert len(fixture.summarizer.calls) == 1

    def test_execute_when_success_then_writes_meta(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request())

        assert len(fixture.metadata_writer.metas_written) == 1
        meta, folder = fixture.metadata_writer.metas_written[0]
        assert meta.author == "XEILOSTRADING"
        assert "2025-03-15" in str(folder)

    def test_execute_then_writes_index(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request())

        assert len(fixture.metadata_writer.index_written) == 1

    def test_execute_then_writes_claude_md(self):
        fixture = Fixture(videos=(_video(),))

        fixture.use_case.execute(_request())

        assert len(fixture.metadata_writer.claude_md_written) == 1

    def test_execute_when_fail_then_skips_meta_for_failed(self):
        fixture = Fixture(videos=_two_videos(), failing_transcriber=True)

        fixture.use_case.execute(_request())

        assert len(fixture.metadata_writer.metas_written) == 0

    def test_execute_creates_per_video_folder_with_date_slug(self):
        fixture = Fixture(videos=(_video(title="My Trading Session", date="20250315"),))

        fixture.use_case.execute(_request())

        _meta, folder = fixture.metadata_writer.metas_written[0]
        assert "2025-03-15" in str(folder)
        assert "my-trading-session" in str(folder)
