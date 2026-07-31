from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_relabeling import merge_labels, relabel_turns

_TURNS = (
    SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
    SpeakerTurn(start=2.0, end=4.0, speaker="SPEAKER_01"),
    SpeakerTurn(start=4.0, end=6.0, speaker="SPEAKER_02"),
)


class TestRelabelTurns:
    def test_relabel_when_mapping_given_then_applied(self):
        result = relabel_turns(_TURNS, {"SPEAKER_02": "SPEAKER_00"})

        assert [t.speaker for t in result] == [
            "SPEAKER_00",
            "SPEAKER_01",
            "SPEAKER_00",
        ]

    def test_relabel_when_empty_mapping_then_unchanged(self):
        assert relabel_turns(_TURNS, {}) == _TURNS

    def test_relabel_when_called_then_bounds_preserved(self):
        result = relabel_turns(_TURNS, {"SPEAKER_02": "SPEAKER_00"})

        assert (result[2].start, result[2].end) == (4.0, 6.0)


class TestMergeLabels:
    def test_merge_when_two_labels_share_a_group_then_mapped_together(self):
        mapping = merge_labels(["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"], [0, 1, 0])

        assert mapping["SPEAKER_00"] == mapping["SPEAKER_02"]
        assert mapping["SPEAKER_01"] != mapping["SPEAKER_00"]

    def test_merge_when_called_then_labels_are_renumbered_from_zero(self):
        mapping = merge_labels(["SPEAKER_03", "SPEAKER_07"], [1, 0])

        assert set(mapping.values()) == {"SPEAKER_00", "SPEAKER_01"}

    def test_merge_when_all_one_group_then_single_label(self):
        mapping = merge_labels(["SPEAKER_00", "SPEAKER_01"], [0, 0])

        assert set(mapping.values()) == {"SPEAKER_00"}
