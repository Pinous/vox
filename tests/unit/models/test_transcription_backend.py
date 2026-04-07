import pytest

from vox.models.exceptions import ValidationError
from vox.models.transcription_backend import TranscriptionBackend


class TestTranscriptionBackendFromString:
    def test_from_string_when_local_then_local(self):
        result = TranscriptionBackend.from_string("local")

        assert result == TranscriptionBackend.LOCAL

    def test_from_string_when_openai_then_openai(self):
        result = TranscriptionBackend.from_string("openai")

        assert result == TranscriptionBackend.OPENAI

    def test_from_string_when_uppercase_then_works(self):
        result = TranscriptionBackend.from_string("OPENAI")

        assert result == TranscriptionBackend.OPENAI

    def test_from_string_when_unknown_then_raises(self):
        with pytest.raises(ValidationError):
            TranscriptionBackend.from_string("invalid")
