from vox.models.segment import Segment
from vox.models.speaker_assignment import assign_speakers
from vox.models.speaker_turn import SpeakerTurn


class TestAssignSpeakers:
    def test_assign_when_no_turns_then_segments_keep_no_speaker(self):
        segments = (Segment(start=0.0, end=2.0, text="hello"),)

        result = assign_speakers(segments, ())

        assert result[0].speaker is None

    def test_assign_when_turn_covers_segment_then_speaker_set(self):
        segments = (Segment(start=1.0, end=2.0, text="hello"),)
        turns = (SpeakerTurn(start=0.0, end=5.0, speaker="SPEAKER_00"),)

        result = assign_speakers(segments, turns)

        assert result[0].speaker == "SPEAKER_00"

    def test_assign_when_segment_straddles_two_turns_then_takes_dominant(self):
        segments = (Segment(start=8.0, end=14.0, text="hello"),)
        turns = (
            SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=10.0, end=20.0, speaker="SPEAKER_01"),
        )

        result = assign_speakers(segments, turns)

        assert result[0].speaker == "SPEAKER_01"

    def test_assign_when_segment_outside_all_turns_then_speaker_is_none(self):
        segments = (Segment(start=30.0, end=31.0, text="hello"),)
        turns = (SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),)

        result = assign_speakers(segments, turns)

        assert result[0].speaker is None

    def test_assign_when_many_segments_then_each_gets_own_speaker(self):
        segments = (
            Segment(start=0.0, end=5.0, text="first"),
            Segment(start=15.0, end=18.0, text="second"),
        )
        turns = (
            SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=10.0, end=20.0, speaker="SPEAKER_01"),
        )

        result = assign_speakers(segments, turns)

        assert [s.speaker for s in result] == ["SPEAKER_00", "SPEAKER_01"]

    def test_assign_when_turns_overlap_then_takes_longest_overlap(self):
        segments = (Segment(start=0.0, end=10.0, text="hello"),)
        turns = (
            SpeakerTurn(start=0.0, end=3.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=2.0, end=10.0, speaker="SPEAKER_01"),
        )

        result = assign_speakers(segments, turns)

        assert result[0].speaker == "SPEAKER_01"

    def test_assign_when_called_then_text_and_bounds_preserved(self):
        segments = (Segment(start=1.0, end=2.0, text="hello"),)
        turns = (SpeakerTurn(start=0.0, end=5.0, speaker="SPEAKER_00"),)

        result = assign_speakers(segments, turns)

        assert (result[0].start, result[0].end, result[0].text) == (1.0, 2.0, "hello")
