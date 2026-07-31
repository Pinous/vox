import pytest

from vox.models.exceptions import ValidationError
from vox.models.speaker_turn import SpeakerTurn


class TestSpeakerTurn:
    def test_create_when_valid_then_fields_set(self):
        turn = SpeakerTurn(start=0.0, end=1.5, speaker="SPEAKER_00")

        assert turn.start == 0.0
        assert turn.end == 1.5
        assert turn.speaker == "SPEAKER_00"

    def test_create_when_negative_start_then_raises(self):
        with pytest.raises(ValidationError, match="start"):
            SpeakerTurn(start=-1.0, end=1.0, speaker="SPEAKER_00")

    def test_create_when_end_before_start_then_raises(self):
        with pytest.raises(ValidationError, match="end"):
            SpeakerTurn(start=2.0, end=1.0, speaker="SPEAKER_00")

    def test_create_when_end_equals_start_then_raises(self):
        with pytest.raises(ValidationError, match="end"):
            SpeakerTurn(start=1.0, end=1.0, speaker="SPEAKER_00")

    def test_create_when_blank_speaker_then_raises(self):
        with pytest.raises(ValidationError, match="speaker"):
            SpeakerTurn(start=0.0, end=1.0, speaker="  ")
