from pathlib import Path

from vox.models.video_metadata import VideoMetadata


class DiskMetadataWriter:
    def write_meta(self, metadata: VideoMetadata, folder: Path) -> None:
        content = _format_meta(metadata)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "meta.md").write_text(content, encoding="utf-8")

    def write_index(
        self, all_metadata: tuple[VideoMetadata, ...], output_dir: Path
    ) -> None:
        content = _format_index(all_metadata)
        (output_dir / "index.md").write_text(content, encoding="utf-8")

    def write_claude_md(self, output_dir: Path) -> None:
        path = output_dir / "CLAUDE.md"
        if path.exists():
            return
        path.write_text(_CLAUDE_MD_CONTENT, encoding="utf-8")


def _format_meta(m: VideoMetadata) -> str:
    lines = [
        f"# {m.title}",
        f"- url: {m.url}",
        f"- author: {m.author}",
        f"- date: {m.date}",
        f"- duration: {m.duration}",
        f"- language: {m.language}",
        f"- topics: {', '.join(m.topics)}",
    ]
    if m.summary:
        lines.append(f"- summary: {m.summary}")
    return "\n".join(lines) + "\n"


def _format_index(all_metadata: tuple[VideoMetadata, ...]) -> str:
    lines = [f"# Transcript index ({len(all_metadata)} videos)\n"]
    for m in sorted(all_metadata, key=lambda x: x.date, reverse=True):
        lines.append(f"## {m.folder_name}")
        lines.append(f"author: {m.author} | topics: {', '.join(m.topics)}")
        if m.summary:
            lines.append(f"summary: {m.summary}")
        lines.append("")
    return "\n".join(lines)


_CLAUDE_MD_CONTENT = """\
# Transcripts Library

This directory contains transcripts of YouTube videos, organized by date and title.

## Structure

- `index.md` — master index of all transcripts with author, topics, and summary
- `YYYY-MM-DD_slug/` — one folder per video containing:
  - `transcript.txt` — plain text transcript
  - `meta.md` — metadata (url, author, date, duration, topics, summary)
  - `transcript.srt` — subtitle file with timestamps
  - `transcript.json` — structured transcript with segments

## How to use

1. Read `index.md` first to find relevant videos by topic or author
2. Dive into a specific folder to read the full transcript
3. Cross-reference multiple transcripts to synthesize insights
"""
