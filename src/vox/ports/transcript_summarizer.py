from typing import Protocol

from vox.models.summary_result import SummaryResult


class TranscriptSummarizer(Protocol):
    def summarize(self, text: str, title: str) -> SummaryResult: ...
