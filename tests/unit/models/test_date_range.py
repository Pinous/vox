import pytest

from vox.models.date_range import DateRange
from vox.models.exceptions import ValidationError


class TestDateRange:
    def test_create_when_valid_then_fields_set(self):
        dr = DateRange(after="20250101", before="20261231")

        assert dr.after == "20250101"
        assert dr.before == "20261231"

    def test_create_when_after_not_8_digits_then_raises(self):
        with pytest.raises(ValidationError, match="after"):
            DateRange(after="2025", before="20261231")

    def test_create_when_before_not_8_digits_then_raises(self):
        with pytest.raises(ValidationError, match="before"):
            DateRange(after="20250101", before="2026")

    def test_create_when_after_greater_than_before_then_raises(self):
        with pytest.raises(ValidationError, match=r"after.*before"):
            DateRange(after="20270101", before="20261231")

    def test_from_years_when_single_year_then_full_year_range(self):
        dr = DateRange.from_years((2025,))

        assert dr.after == "20250101"
        assert dr.before == "20251231"

    def test_from_years_when_multiple_years_then_min_to_max(self):
        dr = DateRange.from_years((2025, 2026))

        assert dr.after == "20250101"
        assert dr.before == "20261231"

    def test_from_years_when_empty_then_raises(self):
        with pytest.raises(ValidationError, match="years"):
            DateRange.from_years(())

    def test_frozen_when_set_field_then_raises(self):
        dr = DateRange(after="20250101", before="20261231")

        with pytest.raises(AttributeError):
            dr.after = "20240101"
