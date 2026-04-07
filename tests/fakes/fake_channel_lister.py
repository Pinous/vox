from vox.models.channel_video import ChannelVideo
from vox.models.date_range import DateRange


class FakeChannelLister:
    def __init__(self, videos: tuple[ChannelVideo, ...] = ()):
        self._videos = videos
        self.list_called_with: tuple[str, DateRange] | None = None

    def list_videos(
        self,
        channel_url: str,
        date_range: DateRange,
    ) -> tuple[ChannelVideo, ...]:
        self.list_called_with = (channel_url, date_range)
        return self._videos
