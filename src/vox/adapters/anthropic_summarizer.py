import json
import os

from vox.models.summary_result import SummaryResult

_MAX_TRANSCRIPT_CHARS = 12000

_SYSTEM_PROMPT = (
    "You extract metadata from video transcripts. "
    "Respond ONLY with valid JSON, no markdown fences."
)

_USER_PROMPT_TEMPLATE = (
    'Video title: "{title}"\n\n'
    "Transcript (truncated):\n{transcript}\n\n"
    "Return JSON with exactly these keys:\n"
    '- "summary": 2-3 sentences summarizing the key points '
    "(in the same language as the transcript)\n"
    '- "topics": array of 3-7 topic keywords '
    "(in the same language as the transcript)\n"
)


class AnthropicSummarizer:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self._model = model
        self._client = _build_client()

    def summarize(self, text: str, title: str) -> SummaryResult:
        truncated = text[:_MAX_TRANSCRIPT_CHARS]
        response = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": _USER_PROMPT_TEMPLATE.format(
                        title=title, transcript=truncated
                    ),
                }
            ],
        )
        return _parse_response(response.content[0].text)


def _build_client():
    import anthropic

    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _parse_response(raw: str) -> SummaryResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return SummaryResult(summary="", topics=())
    return SummaryResult(
        summary=data.get("summary", ""),
        topics=tuple(data.get("topics", ())),
    )
