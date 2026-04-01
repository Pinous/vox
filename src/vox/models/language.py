from __future__ import annotations

from dataclasses import dataclass

from vox.models.exceptions import ValidationError

_SUPPORTED_CODES = frozenset(
    {
        "auto",
        "af",
        "am",
        "ar",
        "as",
        "az",
        "ba",
        "be",
        "bg",
        "bn",
        "bo",
        "br",
        "bs",
        "ca",
        "cs",
        "cy",
        "da",
        "de",
        "el",
        "en",
        "eo",
        "es",
        "et",
        "eu",
        "fa",
        "fi",
        "fo",
        "fr",
        "fy",
        "gd",
        "gl",
        "gu",
        "ha",
        "haw",
        "he",
        "hi",
        "hr",
        "ht",
        "hu",
        "hy",
        "id",
        "is",
        "it",
        "ja",
        "jw",
        "ka",
        "kk",
        "km",
        "kn",
        "ko",
        "la",
        "lb",
        "ln",
        "lo",
        "lt",
        "lv",
        "mg",
        "mi",
        "mk",
        "ml",
        "mn",
        "mr",
        "ms",
        "mt",
        "my",
        "ne",
        "nl",
        "nn",
        "no",
        "oc",
        "pa",
        "pl",
        "ps",
        "pt",
        "ro",
        "ru",
        "sa",
        "sd",
        "si",
        "sk",
        "sl",
        "sn",
        "so",
        "sq",
        "sr",
        "su",
        "sv",
        "sw",
        "ta",
        "te",
        "tg",
        "th",
        "tk",
        "tl",
        "tr",
        "tt",
        "uk",
        "ur",
        "uz",
        "vi",
        "yi",
        "yo",
        "zh",
        "zu",
    }
)


@dataclass(frozen=True)
class Language:
    code: str

    @classmethod
    def from_string(cls, raw: str) -> Language:
        _reject_empty(raw)
        normalized = raw.strip().lower()
        _reject_unsupported(normalized)
        return cls(code=normalized)


def _reject_empty(raw: str) -> None:
    if not raw.strip():
        raise ValidationError("Language code must not be empty")


def _reject_unsupported(code: str) -> None:
    if code not in _SUPPORTED_CODES:
        raise ValidationError(f"Unsupported language code: {code}")
