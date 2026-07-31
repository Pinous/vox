from dataclasses import replace

from vox.models.speaker_turn import SpeakerTurn


def relabel_turns(
    turns: tuple[SpeakerTurn, ...],
    mapping: dict[str, str],
) -> tuple[SpeakerTurn, ...]:
    if not mapping:
        return turns
    return tuple(replace(t, speaker=mapping.get(t.speaker, t.speaker)) for t in turns)


def merge_labels(labels: list[str], groups: list[int]) -> dict[str, str]:
    renumbered = _renumber(groups)
    return {
        label: f"SPEAKER_{renumbered[group]:02d}"
        for label, group in zip(labels, groups, strict=True)
    }


def _renumber(groups: list[int]) -> dict[int, int]:
    order: dict[int, int] = {}
    for group in groups:
        if group not in order:
            order[group] = len(order)
    return order
