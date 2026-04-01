import pytest

from vox.models.exceptions import ValidationError
from vox.models.transcription_input import TranscriptionInput


class TestTranscriptionInput:
    def test_create_when_valid_url_then_is_url_true(self):
        result = TranscriptionInput.from_string("https://example.com/video.mp4")

        assert result.is_url is True
        assert result.source == "https://example.com/video.mp4"

    def test_create_when_valid_file_path_then_is_url_false(self):
        result = TranscriptionInput.from_string("/tmp/audio.mp3")

        assert result.is_url is False
        assert result.source == "/tmp/audio.mp3"

    def test_create_when_empty_string_then_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            TranscriptionInput.from_string("")

    def test_create_when_path_traversal_then_raises(self):
        with pytest.raises(ValidationError, match="path traversal"):
            TranscriptionInput.from_string("/tmp/../etc/passwd.mp3")

    def test_create_when_control_characters_then_raises(self):
        with pytest.raises(ValidationError, match="control character"):
            TranscriptionInput.from_string("/tmp/audio\x00.mp3")

    def test_create_when_ftp_url_then_raises(self):
        with pytest.raises(ValidationError, match="scheme"):
            TranscriptionInput.from_string("ftp://example.com/audio.mp3")

    def test_create_when_unsupported_extension_then_raises(self):
        with pytest.raises(ValidationError, match="extension"):
            TranscriptionInput.from_string("/tmp/document.pdf")

    def test_create_when_mp3_extension_then_succeeds(self):
        result = TranscriptionInput.from_string("/tmp/song.mp3")

        assert result.source == "/tmp/song.mp3"
        assert result.is_url is False

    def test_create_when_url_encoded_path_then_raises(self):
        with pytest.raises(ValidationError, match="URL-encoded"):
            TranscriptionInput.from_string("my%20audio.mp3")

    def test_create_when_https_youtube_url_then_succeeds(self):
        result = TranscriptionInput.from_string(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

        assert result.is_url is True
        assert result.source == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
