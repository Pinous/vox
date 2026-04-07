# ADR-001: Batch YouTube channel transcription with Google Drive upload

**Date**: 2026-04-01
**Status**: Accepted

## Context

`vox` was used to transcribe YouTube videos one at a time. The need
emerged to transcribe an entire channel's videos in bulk, filtered by
year, then push the transcripts to Google Drive without keeping the
audio files locally (limited disk space).

No batch functionality existed. The CLI handled only one URL or file
at a time.

A second need: organize the transcripts as a knowledge base usable by
Claude Code. Each video gets a `meta.md` (author, topics, LLM
summary), and an `index.md` aggregates all the metas so an agent can
search quickly without reading every transcript.

## Decisions

### New `vox channel` command

A dedicated command was created rather than a `--batch` flag on
`transcribe`. The flow is fundamentally different (listing → filter →
loop → summarize → upload → cleanup). Mixing this into `transcribe`
would have violated SRP.

### rclone as upload adapter (not the Google API directly)

Three options were on the table:

1. **OAuth2 + google-api-python-client** — standard but heavy setup
   (Google Cloud project, `client_secret.json`, interactive OAuth flow)
2. **rclone** — already a tool many users have configured, handles
   multi-account Google natively, zero extra Python dependency
3. **Service Account** — no interactive flow but requires explicit
   folder sharing

rclone was chosen because:

- No new Python dependency (subprocess, like yt-dlp and ffmpeg)
- Multi-account Google Drive (e.g. `u/4` in the Drive URL) is handled
  natively by rclone
- Consistent with the rest of the project: external tools are called
  via subprocess adapters

The `FileUploader` port is intentionally generic (not coupled to
rclone). Tomorrow we can plug in S3, Dropbox, or the Google API
directly without touching the use case.

### File organization: knowledge base structure

Local structure:

```
~/transcripts/
├── CLAUDE.md                          ← context for Claude Code
├── index.md                           ← concatenation of every meta.md
├── 2025-03-15_video-slug-1/
│   ├── transcript.txt
│   ├── transcript.srt
│   ├── transcript.json
│   └── meta.md
└── 2025-04-20_video-slug-2/
    ├── transcript.txt
    └── meta.md
```

Remote structure (same hierarchy with the channel name on top):

```
gdrive:Transcripts/<channel>/<Video Title>/
```

Why this structure:

- **One folder per video with date-slug**: chronologically sortable,
  human-readable
- **`meta.md`**: structured metadata (author, topics, summary) for
  fast search
- **`index.md`**: the trick — Claude Code reads this single file and
  knows about every transcript
- **`CLAUDE.md`**: explains the structure to Claude Code automatically

### Summary and topics via Claude CLI (default)

By default, `vox channel` shells out to the `claude` CLI to generate
the summary and topics. This uses the user's Claude subscription — no
API key needed, no extra Python dependency.

The summarizer is pluggable via the `--summarizer` flag:

| Value           | Adapter                                                       | When to use it                                                |
| --------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| `auto` (default)| `ClaudeSummarizer` if `claude` is in PATH, else `NoopSummarizer` | Normal use — works out of the box if Claude Code is installed |
| `claude`        | `ClaudeSummarizer`                                            | Force the Claude CLI                                          |
| `anthropic`     | `AnthropicSummarizer`                                         | Direct API, requires `ANTHROPIC_API_KEY` + `pip install anthropic` |
| `none`          | `NoopSummarizer`                                              | Skip the summary/topics step                                  |

Why this design:

- **Works out of the box**: if you have Claude Code, you have `claude`
  in your PATH, so summary + topics are generated with no config
- **Pluggable**: the `TranscriptSummarizer` port is a Python
  `Protocol`. To add a new backend (OpenAI, Mistral, etc.), create an
  adapter implementing `summarize(text, title) -> SummaryResult` and
  register it in `_build_summarizer()`
- **No forced dependency**: the Anthropic SDK is a lazy import inside
  the adapter, not a project dependency

### Sequential processing (not parallel)

One video at a time: download → clean → transcribe → summarize →
write meta → upload → cleanup → next. Reasons:

- Disk space control (with `--cleanup`, only one video lives on disk
  at a time)
- MLX Whisper uses the GPU — parallelizing would not help
- Simpler debugging and progress tracking

### Tolerance for partial failures

If a video fails (network error, unsupported format, etc.), the error
is recorded and the loop continues. The final `BatchResult` reports
`succeeded/failed`. No `meta.md` is written for failed videos. The
`index.md` only contains successful videos.

## Architecture

```
Models (inner layer)
  ChannelVideo (with duration_seconds), DateRange, BatchResult
  SummaryResult, VideoMetadata
  + exceptions: ChannelListingError, UploadError

Ports (interfaces)
  ChannelLister, FileUploader, FileCleaner
  TranscriptSummarizer, MetadataWriter

Use case
  BatchTranscribeUseCase
    ├── composes TranscribeUseCase (no duplication)
    ├── calls TranscriptSummarizer to enrich
    └── calls MetadataWriter for meta/index/CLAUDE.md

Adapters (outer layer)
  YtdlpChannelLister, RcloneUploader, DiskFileCleaner
  ClaudeSummarizer / AnthropicSummarizer / NoopSummarizer
  DiskMetadataWriter
  CLI: channel_cmd.py (--summarizer auto|claude|anthropic|none)
```

## Files created

| File                                          | Purpose                                              |
| --------------------------------------------- | ---------------------------------------------------- |
| `src/vox/models/channel_video.py`             | YouTube video (id, title, date, channel, duration)  |
| `src/vox/models/date_range.py`                | Year filter (factory `from_years`)                  |
| `src/vox/models/batch_result.py`              | Batch result (per-video success/failure)            |
| `src/vox/models/summary_result.py`            | LLM result (summary + topics)                       |
| `src/vox/models/video_metadata.py`            | Content of `meta.md`                                |
| `src/vox/ports/channel_lister.py`             | Protocol: list a channel's videos                   |
| `src/vox/ports/file_uploader.py`              | Protocol: upload a file (generic)                   |
| `src/vox/ports/file_cleaner.py`               | Protocol: delete a file                             |
| `src/vox/ports/transcript_summarizer.py`      | Protocol: summarize a transcript                    |
| `src/vox/ports/metadata_writer.py`            | Protocol: write meta/index/CLAUDE.md                |
| `src/vox/adapters/ytdlp_channel_lister.py`    | `yt-dlp --flat-playlist --dump-json`                |
| `src/vox/adapters/rclone_uploader.py`         | `rclone copy` to remote                             |
| `src/vox/adapters/disk_file_cleaner.py`       | `path.unlink()`                                     |
| `src/vox/adapters/claude_summarizer.py`       | Claude Sonnet via `claude -p` CLI (subscription)    |
| `src/vox/adapters/anthropic_summarizer.py`    | Claude Sonnet via Anthropic SDK (API key)           |
| `src/vox/adapters/noop_summarizer.py`         | No-op when summary is skipped                       |
| `src/vox/adapters/disk_metadata_writer.py`    | Writes `meta.md`, `index.md`, `CLAUDE.md`           |
| `src/vox/adapters/cli/channel_cmd.py`         | Click command `vox channel`                         |
| `src/vox/use_cases/batch_transcribe.py`       | Batch orchestration                                 |

## Files modified

| File                                | Change                                          |
| ----------------------------------- | ----------------------------------------------- |
| `src/vox/models/exceptions.py`      | +`ChannelListingError`, +`UploadError`          |
| `src/vox/adapters/cli/app.py`       | +`main.add_command(channel)`                    |
| `src/vox/use_cases/transcribe.py`   | +`output_stem` field on `TranscribeRequest`     |

## Consequences

- `vox channel` produces a Claude-Code-ready knowledge base
- By default, summary + topics are generated via the Claude
  subscription (`claude -p` CLI)
- `CLAUDE.md` + `index.md` let Claude navigate the transcripts without
  reading every file
- The `--summarizer` flag makes the LLM backend pluggable (claude,
  anthropic, none, and extensible)
- The `FileUploader` port can be reused for other storage backends
- The `ChannelLister` can be extended to other sources (playlists,
  hashtags, etc.)
- Unit tests cover the use case via fakes (no network, no GPU)
