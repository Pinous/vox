from __future__ import annotations

import re
from dataclasses import dataclass

from vox.models.exceptions import ValidationError

_DATE_PATTERN = re.compile(r"^\d{8}$")


@dataclass(frozen=True)
class ChannelVideo:
    video_id: str
    title: str
    url: str
    upload_date: str
    channel_name: str
    duration_seconds: int = 0

    def __post_init__(self):
        if not self.video_id:
            raise ValidationError("video_id must not be empty")
        if not self.channel_name:
            raise ValidationError("channel_name must not be empty")
        if not _DATE_PATTERN.match(self.upload_date):
            raise ValidationError("upload_date must be 8 digits (YYYYMMDD)")
