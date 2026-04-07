from typing import Protocol

from vox.models.channel_video import ChannelVideo
from vox.models.date_range import DateRange


class ChannelLister(Protocol):
    def list_videos(
        self,
        channel_url: str,
        date_range: DateRange,
    ) -> tuple[ChannelVideo, ...]: ...
