import json
import subprocess
import sys

from vox.models.channel_video import ChannelVideo
from vox.models.date_range import DateRange
from vox.models.exceptions import ChannelListingError


class YtdlpChannelLister:
    def __init__(
        self,
        use_cookies: bool = True,
        sleep_interval: int = 1,
    ):
        self._use_cookies = use_cookies
        self._sleep_interval = sleep_interval

    def list_videos(
        self,
        channel_url: str,
        date_range: DateRange,
    ) -> tuple[ChannelVideo, ...]:
        cmd = self._build_command(channel_url)
        stdout = _run_ytdlp(cmd)
        all_videos = _parse_videos(stdout)
        return _filter_by_date(all_videos, date_range)

    def _build_command(self, channel_url: str) -> list[str]:
        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--dump-json",
            "--skip-download",
            "--js-runtimes",
            "node",
            "--remote-components",
            "ejs:github",
        ]
        if self._use_cookies:
            cmd += ["--cookies-from-browser", "chrome"]
        if self._sleep_interval > 0:
            cmd += ["--sleep-interval", str(self._sleep_interval)]
        cmd.append(channel_url)
        return cmd


def _run_ytdlp(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 and not result.stdout.strip():
        raise ChannelListingError(f"yt-dlp failed: {result.stderr}")
    return result.stdout


def _parse_videos(stdout: str) -> tuple[ChannelVideo, ...]:
    videos = []
    for line in stdout.strip().splitlines():
        if not line.strip():
            continue
        video = _parse_one(line)
        if video:
            videos.append(video)
    return tuple(videos)


def _parse_one(line: str) -> ChannelVideo | None:
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None
    video_id = data.get("id", "")
    if not video_id:
        return None
    return ChannelVideo(
        video_id=video_id,
        title=data.get("title", video_id),
        url=f"https://www.youtube.com/watch?v={video_id}",
        upload_date=data.get("upload_date", "00000000"),
        channel_name=data.get("channel", data.get("uploader", "unknown")),
        duration_seconds=int(data.get("duration", 0) or 0),
    )


def _filter_by_date(
    videos: tuple[ChannelVideo, ...],
    date_range: DateRange,
) -> tuple[ChannelVideo, ...]:
    return tuple(
        v
        for v in videos
        if v.upload_date != "00000000"
        and date_range.after <= v.upload_date <= date_range.before
    )
