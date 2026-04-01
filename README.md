# vox

Agent-first CLI for audio/video transcription via MLX Whisper on Apple Silicon.

## Install

```bash
# From PyPI (coming soon)
pip install vox-transcribe

# From source
git clone https://github.com/Pinous/vox.git
cd vox
uv sync
```

### System dependency

**ffmpeg** is the only system dependency (for audio cleaning):

```bash
brew install ffmpeg
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
| `vox transcribe <source>` | Full transcription pipeline |
| `vox init [-m MODEL]` | Download Whisper model |
| `vox doctor` | Check dependency health |
| `vox schema [COMMAND]` | JSON schema for agent introspection |

## Models

| Model | Quality | Use Case |
|-------|---------|----------|
| tiny | Low | Quick drafts |
| base | Fair | Fast transcription |
| **small** | Good | **Default — balanced** |
| medium | High | Important content |
| large-v3 | Best | Maximum accuracy |

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

## Development

```bash
uv sync
uv run pytest              # Run tests (71 tests)
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
