# vox

[![PyPI](https://img.shields.io/pypi/v/vox-transcribe)](https://pypi.org/project/vox-transcribe/)
[![Python](https://img.shields.io/pypi/pyversions/vox-transcribe)](https://pypi.org/project/vox-transcribe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Local audio/video transcription for macOS. Runs Whisper on Apple Silicon — no cloud, no API keys, no cost per minute.

Agent-first CLI built on [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) for native GPU acceleration.

> **New to the codebase?** Read the [Architecture Guide](ARCHITECTURE.md).

## Install

```bash
# From PyPI (coming soon)
pip install vox-transcribe

# From source
git clone https://github.com/Pinous/vox.git
cd vox
uv sync
```

### System dependencies

```bash
brew install ffmpeg    # audio cleaning (required)
brew install rclone    # Google Drive upload (optional, for vox channel --upload)
```

Everything else (mlx-whisper, yt-dlp) is installed automatically as Python packages.

## Usage

```bash
# Transcribe a local file
vox recording.mp3

# Transcribe a YouTube video
vox transcribe https://youtube.com/watch?v=VIDEO_ID

# French audio with large model
vox transcribe audio.m4a -l fr -m large-v3

# Word-level timestamps
vox transcribe podcast.mp3 --words

# Agent mode: JSON output with specific fields
vox transcribe audio.wav --fields text,language --format json

# Batch transcribe a YouTube channel (filtered by year)
vox channel "https://www.youtube.com/{channel}" \
  --years 2025,2026 -o ~/transcripts

# Same with Google Drive upload + disk cleanup
vox channel "https://www.youtube.com/{channel}" \
  --years 2025,2026 --upload --remote gdrive --remote-folder Transcripts --cleanup

# Use the OpenAI cloud backend (works on Linux/Windows, requires OPENAI_API_KEY)
vox transcribe podcast.mp3 -b openai
vox transcribe interview.wav -b openai -m gpt-4o-mini-transcribe

# Check dependencies
vox doctor

# Download a model ahead of time
vox init -m small

# Get API schema (for AI agents)
vox schema transcribe
```

## Commands

| Command | Description |
|---------|-------------|
| `vox <source>` | Shorthand for `vox transcribe` |
| `vox transcribe <source>` | Full transcription pipeline (use `-b openai` for cloud) |
| `vox channel <url>` | Batch transcribe a YouTube channel |
| `vox init [-m MODEL]` | Download Whisper model |
| `vox doctor` | Check dependency health |
| `vox schema [COMMAND]` | JSON schema for agent introspection |

## Models

### Local backend (default, MLX on Apple Silicon)

| Model | Quality | Use Case |
|-------|---------|----------|
| tiny | Low | Quick drafts |
| base | Fair | Fast transcription |
| **small** | Good | **Default — balanced** |
| medium | High | Important content |
| large-v3 | Best | Maximum accuracy |
| large-v3-turbo | Best | Faster than large-v3, near-identical quality |

### OpenAI backend (cloud, cross-platform)

| Model | Use Case |
|-------|----------|
| **gpt-4o-transcribe** | **Default for `-b openai` — best quality** |
| gpt-4o-mini-transcribe | Faster, cheaper |
| whisper-1 | Returns segment-level timestamps in SRT |

The OpenAI backend requires `OPENAI_API_KEY` and the `openai` Python package
(`uv add openai`). Files are limited to **25 MB** by the OpenAI API. Word-level
timestamps (`--words`) are not supported with this backend.

## Agent-First Design

vox is designed to be used by AI agents (Claude Code, etc.):

- **Auto-detect output**: JSON when piped, table when TTY
- **Field filtering**: `--fields text` returns only the transcript (saves tokens)
- **Schema introspection**: `vox schema transcribe` returns the full API schema
- **Dry-run**: `--dry-run` validates input and shows execution plan
- **JSON payload**: `--json '{"input":"file.mp3","language":"fr"}'`

## Pipeline

```
Input (URL or file)
  → [yt-dlp] Download media (if URL)
  → [ffmpeg] Clean audio (silence removal, denoise, normalize)
  → [mlx-whisper] Transcribe (native Apple Silicon)
  → Output: .srt + .txt + .json
```

## Requirements

- **macOS** with Apple Silicon (M1/M2/M3/M4)
- **Python 3.13+**
- **ffmpeg** (`brew install ffmpeg`)
- **rclone** (`brew install rclone`) — optional, for `vox channel --upload`
- **Node.js** (`brew install node`) — optional, improves yt-dlp compatibility with YouTube

## Development

```bash
uv sync
uv run pytest              # Run tests (107 tests)
uv run ruff check --fix    # Lint
uv run ruff format         # Format
uv run ty check            # Type check
```

## Architecture

Hexagonal architecture (Clean Architecture). See [ARCHITECTURE.md](ARCHITECTURE.md).

```
src/vox/
├── models/       # Value Objects (frozen dataclasses)
├── ports/        # Protocols (interfaces)
├── use_cases/    # Business logic orchestration
├── adapters/     # CLI (Click) + infrastructure (mlx-whisper, ffmpeg, yt-dlp)
└── schemas/      # JSON schemas for agent introspection
```

## Credits

Inspired by [crafter-station/trx](https://github.com/crafter-station/trx) — rewritten in Python with MLX Whisper for native Apple Silicon transcription.

## License

MIT
