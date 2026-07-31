from vox.models.speaker_turn import SpeakerTurn


def longest_turn_per_speaker(
    turns: tuple[SpeakerTurn, ...],
) -> dict[str, SpeakerTurn]:
    longest: dict[str, SpeakerTurn] = {}
    for turn in turns:
        current = longest.get(turn.speaker)
        if current is None or _duration(turn) > _duration(current):
            longest[turn.speaker] = turn
    return longest


def _duration(turn: SpeakerTurn) -> float:
    return turn.end - turn.start
