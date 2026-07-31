from vox.models.voice_matching import cosine_similarity, match_speakers
from vox.models.voice_print import VoicePrint


class TestCosineSimilarity:
    def test_similarity_when_identical_then_one(self):
        assert cosine_similarity((1.0, 0.0), (1.0, 0.0)) == 1.0

    def test_similarity_when_orthogonal_then_zero(self):
        assert cosine_similarity((1.0, 0.0), (0.0, 1.0)) == 0.0

    def test_similarity_when_scaled_then_still_one(self):
        assert cosine_similarity((1.0, 1.0), (3.0, 3.0)) == 1.0

    def test_similarity_when_zero_vector_then_zero(self):
        assert cosine_similarity((0.0, 0.0), (1.0, 1.0)) == 0.0


class TestMatchSpeakers:
    def test_match_when_above_threshold_then_named(self):
        prints = (VoicePrint(name="Coco", embedding=(1.0, 0.0)),)

        mapping = match_speakers({"SPEAKER_00": (1.0, 0.0)}, prints, 0.5)

        assert mapping == {"SPEAKER_00": "Coco"}

    def test_match_when_below_threshold_then_absent(self):
        prints = (VoicePrint(name="Coco", embedding=(1.0, 0.0)),)

        mapping = match_speakers({"SPEAKER_00": (0.0, 1.0)}, prints, 0.5)

        assert mapping == {}

    def test_match_when_several_prints_then_best_wins(self):
        prints = (
            VoicePrint(name="Coco", embedding=(1.0, 0.0)),
            VoicePrint(name="Leslie", embedding=(0.9, 0.4)),
        )

        mapping = match_speakers({"SPEAKER_00": (0.9, 0.4)}, prints, 0.5)

        assert mapping == {"SPEAKER_00": "Leslie"}

    def test_match_when_no_prints_then_empty(self):
        assert match_speakers({"SPEAKER_00": (1.0, 0.0)}, (), 0.5) == {}

    def test_match_when_two_labels_match_same_person_then_both_named(self):
        prints = (VoicePrint(name="Coco", embedding=(1.0, 0.0)),)

        mapping = match_speakers(
            {"SPEAKER_00": (1.0, 0.0), "SPEAKER_01": (0.99, 0.01)}, prints, 0.5
        )

        assert mapping == {"SPEAKER_00": "Coco", "SPEAKER_01": "Coco"}
