from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoMetadata:
    title: str
    url: str
    author: str
    date: str
    duration: str
    language: str
    topics: tuple[str, ...]
    summary: str
    folder_name: str
