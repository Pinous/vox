from __future__ import annotations

import re
from dataclasses import dataclass

from vox.models.exceptions import ValidationError

_URL_ENCODED_PATTERN = re.compile(r"%[0-9A-Fa-f]{2}")

_SUPPORTED_EXTENSIONS = frozenset(
    {
        ".mp3",
        ".mp4",
        ".wav",
        ".m4a",
        ".flac",
        ".ogg",
        ".webm",
        ".mkv",
        ".avi",
        ".mov",
        ".aac",
        ".wma",
        ".opus",
        ".ts",
    }
)


@dataclass(frozen=True)
class TranscriptionInput:
    source: str
    is_url: bool

    @classmethod
    def from_string(cls, raw: str) -> TranscriptionInput:
        _reject_empty(raw)
        _reject_control_characters(raw)
        _reject_path_traversal(raw)
        is_url = _looks_like_url(raw)
        if is_url:
            _validate_url_scheme(raw)
        else:
            _reject_url_encoded(raw)
            _validate_file_extension(raw)
        return cls(source=raw, is_url=is_url)


def _reject_empty(raw: str) -> None:
    if not raw.strip():
        raise ValidationError("Source must not be empty")


def _reject_control_characters(raw: str) -> None:
    if any(ord(c) < 0x20 and c != " " for c in raw):
        raise ValidationError("Source contains a control character")


def _reject_path_traversal(raw: str) -> None:
    if ".." in raw:
        raise ValidationError("Source contains path traversal")


def _looks_like_url(raw: str) -> bool:
    return "://" in raw


def _validate_url_scheme(raw: str) -> None:
    if not raw.startswith(("http://", "https://")):
        raise ValidationError(f"Unsupported URL scheme: {raw}")


def _reject_url_encoded(raw: str) -> None:
    if _URL_ENCODED_PATTERN.search(raw):
        raise ValidationError("File path contains URL-encoded characters")


def _validate_file_extension(raw: str) -> None:
    dot_index = raw.rfind(".")
    if dot_index == -1:
        raise ValidationError(f"Unsupported file extension: {raw}")
    extension = raw[dot_index:].lower()
    if extension not in _SUPPORTED_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension: {extension}")
