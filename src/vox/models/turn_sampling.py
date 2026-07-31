from vox.models.speaker_turn import SpeakerTurn


def longest_turns(
    turns: tuple[SpeakerTurn, ...],
    limit: int,
) -> tuple[SpeakerTurn, ...]:
    ordered = sorted(turns, key=lambda t: t.end - t.start, reverse=True)
    return tuple(ordered[:limit])
