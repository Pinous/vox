from dataclasses import replace

from vox.models.segment import Segment
from vox.models.speaker_turn import SpeakerTurn


def assign_speakers(
    segments: tuple[Segment, ...],
    turns: tuple[SpeakerTurn, ...],
) -> tuple[Segment, ...]:
    if not turns:
        return segments
    return tuple(replace(s, speaker=_dominant_speaker(s, turns)) for s in segments)


def _dominant_speaker(
    segment: Segment,
    turns: tuple[SpeakerTurn, ...],
) -> str | None:
    totals: dict[str, float] = {}
    for turn in turns:
        overlap = _overlap_seconds(segment, turn)
        if overlap > 0:
            totals[turn.speaker] = totals.get(turn.speaker, 0.0) + overlap
    if not totals:
        return None
    return max(totals, key=lambda speaker: totals[speaker])


def _overlap_seconds(segment: Segment, turn: SpeakerTurn) -> float:
    return min(segment.end, turn.end) - max(segment.start, turn.start)
