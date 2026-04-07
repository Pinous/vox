from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryResult:
    summary: str
    topics: tuple[str, ...]
