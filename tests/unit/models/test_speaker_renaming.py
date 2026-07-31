from vox.models.segment import Segment
from vox.models.speaker_renaming import rename_speakers


class TestRenameSpeakers:
    def test_rename_when_mapping_matches_then_speaker_replaced(self):
        segments = (Segment(start=0.0, end=1.0, text="hi", speaker="SPEAKER_00"),)

        result = rename_speakers(segments, {"SPEAKER_00": "Coco"})

        assert result[0].speaker == "Coco"

    def test_rename_when_no_mapping_then_label_kept(self):
        segments = (Segment(start=0.0, end=1.0, text="hi", speaker="SPEAKER_01"),)

        result = rename_speakers(segments, {"SPEAKER_00": "Coco"})

        assert result[0].speaker == "SPEAKER_01"

    def test_rename_when_empty_mapping_then_segments_unchanged(self):
        segments = (Segment(start=0.0, end=1.0, text="hi", speaker="SPEAKER_00"),)

        result = rename_speakers(segments, {})

        assert result == segments

    def test_rename_when_segment_has_no_speaker_then_left_alone(self):
        segments = (Segment(start=0.0, end=1.0, text="hi"),)

        result = rename_speakers(segments, {"SPEAKER_00": "Coco"})

        assert result[0].speaker is None

    def test_rename_when_called_then_text_and_bounds_preserved(self):
        segments = (Segment(start=1.0, end=2.0, text="hi", speaker="SPEAKER_00"),)

        result = rename_speakers(segments, {"SPEAKER_00": "Coco"})

        assert (result[0].start, result[0].end, result[0].text) == (1.0, 2.0, "hi")
