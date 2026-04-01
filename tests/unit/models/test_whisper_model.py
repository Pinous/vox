import pytest

from vox.models.exceptions import ValidationError
from vox.models.whisper_model import WhisperModel


class TestWhisperModelFromString:
    def test_from_string_when_small_then_small_model(self):
        result = WhisperModel.from_string("small")

        assert result == WhisperModel.SMALL

    def test_from_string_when_large_v3_then_large_model(self):
        result = WhisperModel.from_string("large_v3")

        assert result == WhisperModel.LARGE_V3

    def test_from_string_when_large_dash_v3_then_large_model(self):
        result = WhisperModel.from_string("large-v3")

        assert result == WhisperModel.LARGE_V3

    def test_from_string_when_uppercase_then_works(self):
        result = WhisperModel.from_string("SMALL")

        assert result == WhisperModel.SMALL

    def test_from_string_when_unknown_then_raises(self):
        with pytest.raises(ValidationError):
            WhisperModel.from_string("unknown")


class TestWhisperModelHfRepo:
    def test_hf_repo_when_small_then_correct_path(self):
        assert WhisperModel.SMALL.hf_repo == "mlx-community/whisper-small-mlx"

    def test_hf_repo_when_tiny_then_correct_path(self):
        assert WhisperModel.TINY.hf_repo == "mlx-community/whisper-tiny-mlx"
