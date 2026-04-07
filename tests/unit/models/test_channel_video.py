import pytest

from vox.models.channel_video import ChannelVideo
from vox.models.exceptions import ValidationError


class TestChannelVideo:
    def test_create_when_valid_then_fields_set(self):
        video = ChannelVideo(
            video_id="abc123",
            title="Scalping Nasdaq",
            url="https://www.youtube.com/watch?v=abc123",
            upload_date="20250315",
            channel_name="XEILOSTRADING",
        )

        assert video.video_id == "abc123"
        assert video.title == "Scalping Nasdaq"
        assert video.url == "https://www.youtube.com/watch?v=abc123"
        assert video.upload_date == "20250315"
        assert video.channel_name == "XEILOSTRADING"

    def test_create_when_empty_video_id_then_raises(self):
        with pytest.raises(ValidationError, match="video_id"):
            ChannelVideo(
                video_id="",
                title="Scalping",
                url="https://www.youtube.com/watch?v=x",
                upload_date="20250101",
                channel_name="XEILOS",
            )

    def test_create_when_empty_channel_name_then_raises(self):
        with pytest.raises(ValidationError, match="channel_name"):
            ChannelVideo(
                video_id="abc",
                title="Scalping",
                url="https://www.youtube.com/watch?v=abc",
                upload_date="20250101",
                channel_name="",
            )

    def test_create_when_upload_date_not_8_digits_then_raises(self):
        with pytest.raises(ValidationError, match="upload_date"):
            ChannelVideo(
                video_id="abc",
                title="Scalping",
                url="https://www.youtube.com/watch?v=abc",
                upload_date="2025-01",
                channel_name="XEILOS",
            )

    def test_create_when_upload_date_has_letters_then_raises(self):
        with pytest.raises(ValidationError, match="upload_date"):
            ChannelVideo(
                video_id="abc",
                title="Scalping",
                url="https://www.youtube.com/watch?v=abc",
                upload_date="2025abcd",
                channel_name="XEILOS",
            )

    def test_create_when_duration_provided_then_stored(self):
        video = ChannelVideo(
            video_id="abc",
            title="Scalping",
            url="https://www.youtube.com/watch?v=abc",
            upload_date="20250101",
            channel_name="XEILOS",
            duration_seconds=1320,
        )

        assert video.duration_seconds == 1320

    def test_create_when_no_duration_then_defaults_to_zero(self):
        video = ChannelVideo(
            video_id="abc",
            title="Scalping",
            url="https://www.youtube.com/watch?v=abc",
            upload_date="20250101",
            channel_name="XEILOS",
        )

        assert video.duration_seconds == 0

    def test_frozen_when_set_field_then_raises(self):
        video = ChannelVideo(
            video_id="abc",
            title="Scalping",
            url="https://www.youtube.com/watch?v=abc",
            upload_date="20250101",
            channel_name="XEILOS",
        )

        with pytest.raises(AttributeError):
            video.title = "Changed"
