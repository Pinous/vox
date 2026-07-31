import json
from pathlib import Path

from vox.models.transcription_result import TranscriptionResult


class DiskFileWriter:
    def write_srt(self, result: TranscriptionResult, path: Path) -> None:
        path.write_text(_format_srt(result), encoding="utf-8")

    def write_txt(self, result: TranscriptionResult, path: Path) -> None:
        path.write_text(_format_txt(result), encoding="utf-8")

    def write_json(self, result: TranscriptionResult, path: Path) -> None:
        payload = _to_dict(result)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _format_srt(result: TranscriptionResult) -> str:
    blocks = [
        _format_srt_block(index, segment)
        for index, segment in enumerate(result.segments, start=1)
    ]
    return "\n".join(blocks) + "\n"


def _format_srt_block(index: int, segment) -> str:
    start = _seconds_to_srt_timecode(segment.start)
    end = _seconds_to_srt_timecode(segment.end)
    return f"{index}\n{start} --> {end}\n{_labelled_text(segment)}"


def _labelled_text(segment) -> str:
    if segment.speaker is None:
        return segment.text
    return f"[{segment.speaker}] {segment.text}"


def _format_txt(result: TranscriptionResult) -> str:
    if not any(s.speaker for s in result.segments):
        return result.text
    return "\n\n".join(
        f"{speaker}: {text}" for speaker, text in _group_by_speaker(result.segments)
    )


def _group_by_speaker(segments) -> list[tuple[str, str]]:
    blocks: list[tuple[str, list[str]]] = []
    for segment in segments:
        speaker = segment.speaker or "UNKNOWN"
        if blocks and blocks[-1][0] == speaker:
            blocks[-1][1].append(segment.text.strip())
        else:
            blocks.append((speaker, [segment.text.strip()]))
    return [(speaker, " ".join(parts)) for speaker, parts in blocks]


def _seconds_to_srt_timecode(seconds: float) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    millis = round((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _to_dict(result: TranscriptionResult) -> dict:
    return {
        "text": result.text,
        "language": result.language,
        "segments": [_segment_to_dict(s) for s in result.segments],
        "words": _words_to_list(result.words),
    }


def _segment_to_dict(segment) -> dict:
    return {
        "start": segment.start,
        "end": segment.end,
        "text": segment.text,
        "speaker": segment.speaker,
    }


def _words_to_list(words) -> list[dict] | None:
    if words is None:
        return None
    return [
        {
            "start": w.start,
            "end": w.end,
            "word": w.word,
            "probability": w.probability,
        }
        for w in words
    ]
