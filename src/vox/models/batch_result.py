from __future__ import annotations

from dataclasses import dataclass

from vox.models.channel_video import ChannelVideo


@dataclass(frozen=True)
class BatchItemResult:
    video: ChannelVideo
    success: bool
    transcript_text: str | None
    error: str | None


@dataclass(frozen=True)
class BatchResult:
    total: int
    succeeded: int
    failed: int
    items: tuple[BatchItemResult, ...]
