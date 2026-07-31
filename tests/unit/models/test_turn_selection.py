from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_selection import longest_turn_per_speaker


class TestLongestTurnPerSpeaker:
    def test_select_when_one_turn_each_then_returns_both(self):
        turns = (
            SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=2.0, end=5.0, speaker="SPEAKER_01"),
        )

        selected = longest_turn_per_speaker(turns)

        assert set(selected) == {"SPEAKER_00", "SPEAKER_01"}

    def test_select_when_several_turns_then_keeps_longest(self):
        turns = (
            SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=10.0, end=20.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=25.0, end=26.0, speaker="SPEAKER_00"),
        )

        selected = longest_turn_per_speaker(turns)

        assert selected["SPEAKER_00"].start == 10.0
        assert selected["SPEAKER_00"].end == 20.0

    def test_select_when_empty_then_empty_dict(self):
        assert longest_turn_per_speaker(()) == {}
