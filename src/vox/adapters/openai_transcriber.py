import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from vox.models.exceptions import TranscriptionError, ValidationError
from vox.models.openai_model import OpenAIModel
from vox.models.segment import Segment
from vox.models.transcription_result import TranscriptionResult

_MAX_FILE_SIZE = 25 * 1024 * 1024
_FALLBACK_DURATION = 1.0


class OpenAITranscriber:
    def __init__(
        self,
        api_caller: Callable | None = None,
        duration_probe: Callable[[Path], float] | None = None,
    ):
        self._api_caller = api_caller or _default_api_caller
        self._duration_probe = duration_probe or _ffprobe_duration

    def transcribe(
        self,
        audio_path: Path,
        model: str,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult:
        _reject_word_timestamps(word_timestamps)
        _reject_oversized(audio_path)
        resolved = OpenAIModel.from_string(model)
        response = _call_api(self._api_caller, audio_path, resolved, language)
        return _to_result(response, audio_path, self._duration_probe)


def _reject_word_timestamps(word_timestamps: bool) -> None:
    if word_timestamps:
        raise ValidationError(
            "word-level timestamps are not supported with the OpenAI backend"
        )


def _reject_oversized(audio_path: Path) -> None:
    size = audio_path.stat().st_size
    if size > _MAX_FILE_SIZE:
        size_mb = size / 1024 / 1024
        raise ValidationError(
            f"file is {size_mb:.1f} MB — OpenAI API limit is 25 MB. "
            "Use --backend local for large files."
        )


def _call_api(
    caller: Callable,
    audio_path: Path,
    model: OpenAIModel,
    language: str | None,
) -> Any:
    try:
        return caller(audio_path, model.api_name, language)
    except Exception as e:
        raise TranscriptionError(str(e)) from e


def _to_result(
    response: Any,
    audio_path: Path,
    duration_probe: Callable[[Path], float],
) -> TranscriptionResult:
    text = getattr(response, "text", "")
    language = getattr(response, "language", "") or ""
    raw_segments = getattr(response, "segments", ()) or ()
    segments = _map_segments(raw_segments, text, audio_path, duration_probe)
    return TranscriptionResult(
        text=text,
        segments=segments,
        language=language,
    )


def _map_segments(
    raw_segments: tuple,
    fallback_text: str,
    audio_path: Path,
    duration_probe: Callable[[Path], float],
) -> tuple[Segment, ...]:
    if not raw_segments:
        duration = duration_probe(audio_path) or _FALLBACK_DURATION
        return (Segment(start=0.0, end=duration, text=fallback_text),)
    return tuple(
        Segment(
            start=_get(seg, "start"),
            end=_get(seg, "end"),
            text=_get(seg, "text"),
        )
        for seg in raw_segments
    )


def _get(seg: Any, key: str) -> Any:
    if isinstance(seg, dict):
        return seg[key]
    return getattr(seg, key)


def _ffprobe_duration(audio_path: Path) -> float:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 0.0
    if result.returncode != 0:
        return 0.0
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _default_api_caller(
    audio_path: Path,
    model_api_name: str,
    language: str | None,
) -> Any:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValidationError(
            "OPENAI_API_KEY not set. Export it: export OPENAI_API_KEY=sk-..."
        )
    try:
        from openai import OpenAI
    except ImportError as e:
        raise ValidationError("openai package not installed. Run: uv add openai") from e
    client = OpenAI(api_key=api_key)
    kwargs: dict = {
        "model": model_api_name,
        "response_format": "verbose_json" if model_api_name == "whisper-1" else "json",
    }
    if language and language != "auto":
        kwargs["language"] = language
    with audio_path.open("rb") as f:
        return client.audio.transcriptions.create(file=f, **kwargs)
