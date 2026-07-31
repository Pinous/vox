from vox.models.speaker_count import estimate_speaker_count


class TestEstimateSpeakerCount:
    def test_estimate_when_two_distinct_voices_then_two(self):
        points = [(1.0, 0.0), (0.97, 0.05), (0.0, 1.0), (0.05, 0.97)]

        assert estimate_speaker_count(points) == 2

    def test_estimate_when_three_distinct_voices_then_three(self):
        points = [
            (1.0, 0.0, 0.0),
            (0.97, 0.05, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.97, 0.05),
            (0.0, 0.0, 1.0),
            (0.05, 0.0, 0.97),
        ]

        assert estimate_speaker_count(points) == 3

    def test_estimate_when_all_the_same_voice_then_one(self):
        points = [(1.0, 0.0), (0.999, 0.01), (0.998, 0.02), (1.0, 0.005)]

        assert estimate_speaker_count(points) == 1

    def test_estimate_when_single_point_then_one(self):
        assert estimate_speaker_count([(1.0, 0.0)]) == 1

    def test_estimate_when_empty_then_one(self):
        assert estimate_speaker_count([]) == 1

    def test_estimate_when_max_speakers_caps_then_respects_it(self):
        points = [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.7, 0.7, 0.0),
        ]

        assert estimate_speaker_count(points, max_speakers=2) <= 2
