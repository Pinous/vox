from vox.models.summary_result import SummaryResult


class NoopSummarizer:
    def summarize(self, text: str, title: str) -> SummaryResult:
        return SummaryResult(summary="", topics=())
