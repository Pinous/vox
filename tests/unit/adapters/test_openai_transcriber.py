from dataclasses import dataclass
from pathlib import Path

import pytest

from vox.adapters.openai_transcriber import OpenAITranscriber
from vox.models.exceptions import TranscriptionError, ValidationError


@dataclass
class FakeApiResponse:
    text: str = "hello world"
    language: str = "en"
    segments: tuple = ()


class FakeApiCaller:
    def __init__(self, response=None, raise_exc=None):
        self._response = response or FakeApiResponse()
        self._raise_exc = raise_exc
        self.called_with: tuple | None = None

    def __call__(self, audio_path, model_api_name, language):
        self.called_with = (audio_path, model_api_name, language)
        if self._raise_exc:
            raise self._raise_exc
        return self._response


def _make_audio_file(tmp_path: Path, size_bytes: int = 100) -> Path:
    path = tmp_path / "audio.wav"
    path.write_bytes(b"x" * size_bytes)
    return path


class TestOpenAITranscriberTranscribe:
    def test_transcribe_when_valid_then_returns_text(self, tmp_path):
        caller = FakeApiCaller(FakeApiResponse(text="hello", language="en"))
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        result = transcriber.transcribe(audio, "gpt-4o-transcribe", "en", False)

        assert result.text == "hello"
        assert result.language == "en"

    def test_transcribe_when_called_then_passes_api_name_to_caller(self, tmp_path):
        caller = FakeApiCaller()
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        transcriber.transcribe(audio, "gpt-4o-mini-transcribe", "fr", False)

        assert caller.called_with is not None
        _path, model_name, language = caller.called_with
        assert model_name == "gpt-4o-mini-transcribe"
        assert language == "fr"

    def test_transcribe_when_unknown_model_then_raises(self, tmp_path):
        caller = FakeApiCaller()
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        with pytest.raises(ValidationError, match="Unknown OpenAI model"):
            transcriber.transcribe(audio, "invalid", "en", False)

    def test_transcribe_when_word_timestamps_then_raises(self, tmp_path):
        caller = FakeApiCaller()
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        with pytest.raises(ValidationError, match="word"):
            transcriber.transcribe(audio, "gpt-4o-transcribe", "en", True)

    def test_transcribe_when_file_too_large_then_raises(self, tmp_path):
        caller = FakeApiCaller()
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path, size_bytes=26 * 1024 * 1024)

        with pytest.raises(ValidationError, match="25 MB"):
            transcriber.transcribe(audio, "gpt-4o-transcribe", "en", False)

    def test_transcribe_when_api_call_fails_then_raises_transcription_error(
        self, tmp_path
    ):
        caller = FakeApiCaller(raise_exc=RuntimeError("API down"))
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        with pytest.raises(TranscriptionError, match="API down"):
            transcriber.transcribe(audio, "gpt-4o-transcribe", "en", False)

    def test_transcribe_when_response_has_segments_then_maps_to_result(self, tmp_path):
        segments = (
            {"start": 0.0, "end": 1.5, "text": "hello"},
            {"start": 1.5, "end": 3.0, "text": "world"},
        )
        caller = FakeApiCaller(
            FakeApiResponse(text="hello world", language="en", segments=segments)
        )
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        result = transcriber.transcribe(audio, "whisper-1", "en", False)

        assert len(result.segments) == 2
        assert result.segments[0].text == "hello"
        assert result.segments[1].start == 1.5

    def test_transcribe_when_no_segments_then_single_segment_with_full_text(
        self, tmp_path
    ):
        caller = FakeApiCaller(FakeApiResponse(text="full transcript", language="en"))
        transcriber = OpenAITranscriber(api_caller=caller)
        audio = _make_audio_file(tmp_path)

        result = transcriber.transcribe(audio, "gpt-4o-transcribe", "en", False)

        assert len(result.segments) == 1
        assert result.segments[0].text == "full transcript"
