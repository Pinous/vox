from dataclasses import replace

from vox.models.segment import Segment


def rename_speakers(
    segments: tuple[Segment, ...],
    mapping: dict[str, str],
) -> tuple[Segment, ...]:
    if not mapping:
        return segments
    return tuple(replace(s, speaker=_renamed(s.speaker, mapping)) for s in segments)


def _renamed(speaker: str | None, mapping: dict[str, str]) -> str | None:
    if speaker is None:
        return None
    return mapping.get(speaker, speaker)
