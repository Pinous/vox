from vox.models.summary_result import SummaryResult


class FakeSummarizer:
    def __init__(
        self,
        result: SummaryResult | None = None,
    ):
        self._result = result or SummaryResult(
            summary="Fake summary of the video.",
            topics=("topic1", "topic2"),
        )
        self.calls: list[tuple[str, str]] = []

    def summarize(self, text: str, title: str) -> SummaryResult:
        self.calls.append((text, title))
        return self._result
