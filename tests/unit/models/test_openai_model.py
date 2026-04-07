import pytest

from vox.models.exceptions import ValidationError
from vox.models.openai_model import OpenAIModel


class TestOpenAIModelFromString:
    def test_from_string_when_gpt_4o_transcribe_then_returns_default(self):
        result = OpenAIModel.from_string("gpt-4o-transcribe")

        assert result == OpenAIModel.GPT_4O_TRANSCRIBE

    def test_from_string_when_gpt_4o_mini_then_returns_mini(self):
        result = OpenAIModel.from_string("gpt-4o-mini-transcribe")

        assert result == OpenAIModel.GPT_4O_MINI_TRANSCRIBE

    def test_from_string_when_whisper_1_then_returns_whisper_1(self):
        result = OpenAIModel.from_string("whisper-1")

        assert result == OpenAIModel.WHISPER_1

    def test_from_string_when_unknown_then_raises(self):
        with pytest.raises(ValidationError):
            OpenAIModel.from_string("not-a-real-model")


class TestOpenAIModelApiName:
    def test_api_name_when_gpt_4o_transcribe_then_returns_string(self):
        assert OpenAIModel.GPT_4O_TRANSCRIBE.api_name == "gpt-4o-transcribe"

    def test_api_name_when_whisper_1_then_returns_string(self):
        assert OpenAIModel.WHISPER_1.api_name == "whisper-1"


class TestOpenAIModelSupportsSegments:
    def test_supports_segments_when_whisper_1_then_true(self):
        assert OpenAIModel.WHISPER_1.supports_segments is True

    def test_supports_segments_when_gpt_4o_then_false(self):
        assert OpenAIModel.GPT_4O_TRANSCRIBE.supports_segments is False
