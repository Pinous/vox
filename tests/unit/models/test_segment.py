import pytest

from vox.models.exceptions import ValidationError
from vox.models.segment import Segment


class TestSegment:
    def test_create_when_valid_then_fields_set(self):
        segment = Segment(start=0.0, end=1.5, text="hello")

        assert segment.start == 0.0
        assert segment.end == 1.5
        assert segment.text == "hello"

    def test_create_when_negative_start_then_raises(self):
        with pytest.raises(ValidationError, match="start"):
            Segment(start=-1.0, end=1.0, text="hello")

    def test_create_when_end_before_start_then_raises(self):
        with pytest.raises(ValidationError, match="end"):
            Segment(start=2.0, end=1.0, text="hello")

    def test_create_when_end_equals_start_then_raises(self):
        with pytest.raises(ValidationError, match="end"):
            Segment(start=1.0, end=1.0, text="hello")
