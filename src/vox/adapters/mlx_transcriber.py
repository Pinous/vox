from pathlib import Path

import mlx_whisper

from vox.models.exceptions import TranscriptionError
from vox.models.segment import Segment
from vox.models.transcription_result import TranscriptionResult
from vox.models.whisper_model import WhisperModel
from vox.models.word import Word


class MlxTranscriber:
    def transcribe(
        self,
        audio_path: Path,
        model: str,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult:
        resolved = WhisperModel.from_string(model)
        raw = _call_mlx(audio_path, resolved, language, word_timestamps)
        return _to_result(raw, word_timestamps)


def _call_mlx(
    audio_path: Path,
    model: WhisperModel,
    language: str | None,
    word_timestamps: bool,
) -> dict:
    kwargs = _build_kwargs(model, language, word_timestamps)
    try:
        return mlx_whisper.transcribe(str(audio_path), **kwargs)
    except Exception as e:
        raise TranscriptionError(str(e)) from e


def _build_kwargs(
    model: WhisperModel,
    language: str | None,
    word_timestamps: bool,
) -> dict:
    kwargs: dict = {
        "path_or_hf_repo": model.hf_repo,
        "word_timestamps": word_timestamps,
    }
    if language and language != "auto":
        kwargs["language"] = language
    return kwargs


def _to_result(
    raw: dict,
    word_timestamps: bool,
) -> TranscriptionResult:
    segments = _map_segments(raw["segments"])
    words = _map_all_words(raw["segments"]) if word_timestamps else None
    return TranscriptionResult(
        text=raw["text"],
        segments=segments,
        language=raw["language"],
        words=words,
    )


def _map_segments(raw_segments: list[dict]) -> tuple[Segment, ...]:
    return tuple(
        Segment(start=s["start"], end=s["end"], text=s["text"])
        for s in raw_segments
        if s["end"] > s["start"]
    )


def _map_all_words(raw_segments: list[dict]) -> tuple[Word, ...]:
    return tuple(
        Word(
            start=w["start"],
            end=w["end"],
            word=w["word"],
            probability=w["probability"],
        )
        for s in raw_segments
        for w in s.get("words", [])
        if w["end"] > w["start"]
    )
