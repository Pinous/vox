import pytest

from vox.models.batch_result import BatchItemResult, BatchResult
from vox.models.channel_video import ChannelVideo


def _video(video_id="abc"):
    return ChannelVideo(
        video_id=video_id,
        title="Test",
        url=f"https://www.youtube.com/watch?v={video_id}",
        upload_date="20250101",
        channel_name="TEST",
    )


class TestBatchItemResult:
    def test_create_success_item(self):
        item = BatchItemResult(
            video=_video(),
            success=True,
            transcript_text="Hello world",
            error=None,
        )

        assert item.success is True
        assert item.transcript_text == "Hello world"
        assert item.error is None

    def test_create_failure_item(self):
        item = BatchItemResult(
            video=_video(),
            success=False,
            transcript_text=None,
            error="Download failed",
        )

        assert item.success is False
        assert item.transcript_text is None
        assert item.error == "Download failed"

    def test_frozen_when_set_field_then_raises(self):
        item = BatchItemResult(
            video=_video(), success=True, transcript_text="Hi", error=None
        )

        with pytest.raises(AttributeError):
            item.success = False


class TestBatchResult:
    def test_create_when_valid_then_fields_set(self):
        items = (
            BatchItemResult(
                video=_video("a"), success=True, transcript_text="Hi", error=None
            ),
            BatchItemResult(
                video=_video("b"), success=False, transcript_text=None, error="Fail"
            ),
        )
        result = BatchResult(total=2, succeeded=1, failed=1, items=items)

        assert result.total == 2
        assert result.succeeded == 1
        assert result.failed == 1
        assert len(result.items) == 2

    def test_frozen_when_set_field_then_raises(self):
        result = BatchResult(total=0, succeeded=0, failed=0, items=())

        with pytest.raises(AttributeError):
            result.total = 5
