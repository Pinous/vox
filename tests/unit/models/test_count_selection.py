from vox.models.count_selection import pick_speaker_count

# Silhouette scores actually measured on a 36-minute recording holding
# three speakers: the plain maximum picks 2 and merges two people.
_REAL_RECORDING = {2: 0.6967, 3: 0.5290, 4: 0.3696, 5: 0.3354, 6: 0.3113}

_CLEAR_PAIR = {2: 0.9500, 3: 0.4000, 4: 0.3000}


class TestPickSpeakerCount:
    def test_pick_when_close_runner_up_then_prefers_the_finer_split(self):
        assert pick_speaker_count(_REAL_RECORDING, tolerance=0.70) == 3

    def test_pick_when_runner_up_is_far_behind_then_keeps_the_best(self):
        assert pick_speaker_count(_CLEAR_PAIR, tolerance=0.70) == 2

    def test_pick_when_tolerance_is_one_then_behaves_like_plain_maximum(self):
        assert pick_speaker_count(_REAL_RECORDING, tolerance=1.0) == 2

    def test_pick_when_empty_then_one(self):
        assert pick_speaker_count({}, tolerance=0.70) == 1

    def test_pick_when_all_scores_are_zero_then_one(self):
        assert pick_speaker_count({2: 0.0, 3: 0.0}, tolerance=0.70) == 1

    def test_pick_when_scores_are_negative_then_one(self):
        assert pick_speaker_count({2: -0.3, 3: -0.5}, tolerance=0.70) == 1

    def test_pick_when_several_within_tolerance_then_takes_the_largest(self):
        scores = {2: 1.0, 3: 0.95, 4: 0.90, 5: 0.10}

        assert pick_speaker_count(scores, tolerance=0.70) == 4
