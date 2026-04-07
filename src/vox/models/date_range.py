from __future__ import annotations

import re
from dataclasses import dataclass

from vox.models.exceptions import ValidationError

_DATE_PATTERN = re.compile(r"^\d{8}$")


@dataclass(frozen=True)
class DateRange:
    after: str
    before: str

    def __post_init__(self):
        if not _DATE_PATTERN.match(self.after):
            raise ValidationError("after must be 8 digits (YYYYMMDD)")
        if not _DATE_PATTERN.match(self.before):
            raise ValidationError("before must be 8 digits (YYYYMMDD)")
        if self.after > self.before:
            raise ValidationError("after must not be greater than before")

    @classmethod
    def from_years(cls, years: tuple[int, ...]) -> DateRange:
        if not years:
            raise ValidationError("years must not be empty")
        return cls(
            after=f"{min(years)}0101",
            before=f"{max(years)}1231",
        )
