from types import SimpleNamespace

from vox.adapters.sherpa_diarizer import _speaker_label, _to_turns


def _raw_segment(start, end, speaker):
    return SimpleNamespace(start=start, end=end, speaker=speaker)


class TestSpeakerLabel:
    def test_label_when_zero_then_padded(self):
        assert _speaker_label(0) == "SPEAKER_00"

    def test_label_when_two_digits_then_not_padded(self):
        assert _speaker_label(12) == "SPEAKER_12"


class TestToTurns:
    def test_to_turns_when_segments_then_maps_fields(self):
        raw = [_raw_segment(0.0, 2.5, 0), _raw_segment(2.5, 4.0, 1)]

        turns = _to_turns(raw)

        assert len(turns) == 2
        assert turns[0].start == 0.0
        assert turns[0].end == 2.5
        assert turns[0].speaker == "SPEAKER_00"
        assert turns[1].speaker == "SPEAKER_01"

    def test_to_turns_when_zero_length_segment_then_skipped(self):
        raw = [_raw_segment(1.0, 1.0, 0), _raw_segment(1.0, 2.0, 0)]

        turns = _to_turns(raw)

        assert len(turns) == 1

    def test_to_turns_when_empty_then_returns_empty_tuple(self):
        assert _to_turns([]) == ()
