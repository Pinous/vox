from vox.models.speaker_turn import SpeakerTurn
from vox.models.turn_sampling import longest_turns


def _turn(start, end, speaker="SPEAKER_00"):
    return SpeakerTurn(start=start, end=end, speaker=speaker)


class TestLongestTurns:
    def test_sample_when_fewer_than_limit_then_all_returned(self):
        turns = (_turn(0.0, 1.0), _turn(2.0, 5.0))

        assert len(longest_turns(turns, limit=10)) == 2

    def test_sample_when_more_than_limit_then_capped(self):
        turns = tuple(_turn(i, i + 1) for i in range(100))

        assert len(longest_turns(turns, limit=40)) == 40

    def test_sample_when_capped_then_keeps_the_longest(self):
        turns = (_turn(0.0, 1.0), _turn(10.0, 40.0), _turn(50.0, 51.0))

        sampled = longest_turns(turns, limit=1)

        assert sampled[0].start == 10.0

    def test_sample_when_called_then_ordered_by_duration_desc(self):
        turns = (_turn(0.0, 1.0), _turn(10.0, 40.0), _turn(50.0, 55.0))

        sampled = longest_turns(turns, limit=3)

        durations = [t.end - t.start for t in sampled]
        assert durations == sorted(durations, reverse=True)

    def test_sample_when_empty_then_empty(self):
        assert longest_turns((), limit=10) == ()
