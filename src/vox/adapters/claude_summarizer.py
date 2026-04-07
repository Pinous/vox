import json
import subprocess

from vox.models.summary_result import SummaryResult

_MAX_TRANSCRIPT_CHARS = 12000

_PROMPT_TEMPLATE = (
    'Video title: "{title}"\n\n'
    "Transcript (truncated):\n{transcript}\n\n"
    "Return ONLY valid JSON (no markdown fences) with exactly:\n"
    '- "summary": 2-3 sentences summarizing the key points '
    "(same language as transcript)\n"
    '- "topics": array of 3-7 topic keywords '
    "(same language as transcript)"
)


class ClaudeSummarizer:
    def summarize(self, text: str, title: str) -> SummaryResult:
        truncated = text[:_MAX_TRANSCRIPT_CHARS]
        prompt = _PROMPT_TEMPLATE.format(title=title, transcript=truncated)
        stdout = _run_claude(prompt)
        return _parse_response(stdout)


def _run_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "claude-sonnet-4-6"],
            input=prompt,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _parse_response(raw: str) -> SummaryResult:
    cleaned = _strip_markdown_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return SummaryResult(summary="", topics=())
    return SummaryResult(
        summary=data.get("summary", ""),
        topics=tuple(data.get("topics", ())),
    )


def _strip_markdown_fences(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)
