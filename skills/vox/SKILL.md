# vox — Audio/Video Transcription

Agent-first CLI for transcribing audio/video files using MLX Whisper on Apple Silicon.

## When to Activate

- User wants to transcribe a video or audio file
- User shares a YouTube, Twitter, or Instagram URL
- User says "transcribe", "subtitles", "srt", "transcript"
- User wants to fix or clean up a whisper transcription
- User asks to extract text from video or audio

## Workflow

### 1. Dry-run first (validate before executing)
```bash
vox transcribe <input> --dry-run --format json
```

### 2. Transcribe
```bash
# Local file
vox transcribe recording.mp3 --format json

# URL
vox transcribe https://youtube.com/watch?v=VIDEO_ID --format json

# With options
vox transcribe audio.m4a -l fr -m large-v3 --words --format json

# Agent-optimized: text only (saves tokens)
vox transcribe audio.wav --fields text --format json
```

### 3. Post-process the transcript

Read `references/whisper-fixes.md` before correcting anything. It ranks every
correction by measured frequency over a 1.8M-word French corpus, and — just as
importantly — lists the categories that look obvious but are empty in practice.

Apply in this order, highest volume first:

1. **Delete silence hallucinations** — subtitling boilerplate (`Sous-titrage ...`,
   isolated `Merci.`) emitted over silent stretches. Found in 73 of 227 files.
2. **Collapse decoder repetition loops** — detect by run length (≥5 identical
   consecutive tokens, pinning at 221–223), never by vocabulary.
3. **Fix domain vocabulary** — brand and instrument names are where Whisper fails,
   not general anglicisms.
4. **Dedupe segment boundaries** — 1.29% of boundaries repeat a word, and this
   leaks into the concatenated `text` field.
5. **Re-punctuate and recapitalize only where measured as degraded** — most files
   are fine; a minority have zero periods and no uppercase at all.
6. **Normalize hyphenation and number formats** for consistency.

Do NOT strip filler words (Whisper already removes them: 296 `euh` per 1.8M words)
and do NOT apply broad homophone rules (>90% false positives). Insert
`[Speaker Name]:` markers only when speakers are clearly identifiable.

When editing `.srt`, preserve timestamps, sequence numbers and block count.

### 4. Batch transcribe a channel
```bash
# Dry-run first
vox channel "https://www.youtube.com/@ChannelName" --years 2025 --dry-run --format json

# Transcribe + upload to Google Drive
vox channel "https://www.youtube.com/@ChannelName" \
  --years 2025,2026 -o ~/transcripts \
  --upload --remote gdrive --remote-folder Transcripts --format json

# Without summarization
vox channel "https://www.youtube.com/@ChannelName" --years 2025 --summarizer none --format json
```

### 5. Schema introspection
```bash
vox schema transcribe
vox schema init
```

## Commands

| Command | Purpose |
|---------|---------|
| `vox <source>` | Shorthand for `vox transcribe` |
| `vox transcribe <source>` | Full transcription pipeline |
| `vox channel <url>` | Batch transcribe a YouTube channel |
| `vox init [-m MODEL] [-l LANG]` | Download Whisper model + check deps |
| `vox doctor` | Check dependencies health |
| `vox schema [COMMAND]` | JSON schema for agent introspection |
| `vox --version` | Print the installed version |

## Transcribe Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-l, --language` | string | auto | ISO 639-1 code or 'auto' |
| `-m, --model` | string | small | tiny, base, small, medium, large-v3, large-v3-turbo |
| `-o, --output-dir` | string | . | Output directory |
| `-w, --words` | boolean | false | Word-level timestamps in SRT |
| `--fields` | string | all | Comma-separated: text, language, srt_path, txt_path, json_path, wav_path |
| `--dry-run` | boolean | false | Show execution plan without transcribing |
| `--format` | string | auto | json (piped) or table (TTY) |
| `--no-clean` | boolean | false | Skip ffmpeg audio cleaning |
| `--no-download` | boolean | false | Skip yt-dlp (local files only) |
| `--no-cookies` | boolean | false | Don't send browser cookies to yt-dlp |
| `--browser` | string | chrome | Browser to read cookies from (safari, firefox, edge, brave) |
| `-b, --backend` | string | local | local (MLX) or openai (cloud API, requires OPENAI_API_KEY) |
| `--json` | string | - | Raw JSON payload: {"input", "language", "model"} |

## Channel Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--years` | string | required | Comma-separated years (e.g. 2025,2026) |
| `-l, --language` | string | auto | ISO 639-1 code or 'auto' |
| `-m, --model` | string | small | tiny, base, small, medium, large-v3, large-v3-turbo |
| `-o, --output-dir` | string | . | Output directory |
| `--upload` | boolean | false | Upload via rclone after transcription |
| `--remote` | string | "" | rclone remote name |
| `--remote-folder` | string | "" | Remote folder path |
| `--no-cleanup` | boolean | false | Keep audio files after upload |
| `--no-cookies` | boolean | false | Don't use browser cookies for yt-dlp |
| `--browser` | string | chrome | Browser to read cookies from (safari, firefox, edge, brave) |
| `--sleep` | int | 1 | Seconds between requests |
| `--limit` | int | 0 | Max videos to process (0=all) |
| `--dry-run` | boolean | false | Show execution plan without running |
| `--summarizer` | string | auto | auto, claude, anthropic, none |
| `--no-clean` | boolean | false | Skip ffmpeg audio cleaning |
| `--format` | string | auto | json or table |

## Output Formats

- `--format json`: Machine-readable JSON (default when piped)
- `--format table`: Human-readable key-value (default in TTY)
- `--fields text`: Text only (token-efficient for agents)
- `--fields text,language`: Multiple fields

## Pipeline

```
Input (URL or file)
  → [yt-dlp] Download media (if URL, unless --no-download)
  → [ffmpeg] Clean audio (unless --no-clean):
      silence removal, denoise, normalize, resample 16kHz mono
  → [mlx-whisper] Transcribe with selected model
  → Output: {stem}.srt + {stem}.txt + {stem}.json
```

## Models

| Model | Quality | Speed | Use Case |
|-------|---------|-------|----------|
| tiny | Low | Fastest | Quick drafts, real-time |
| base | Fair | Fast | Quick transcription |
| small | Good | Balanced | **Default — recommended** |
| medium | High | Slow | Important content |
| large-v3 | Best | Slowest | Maximum accuracy |
| large-v3-turbo | Best | Fast | Near-identical to large-v3, faster |

## Supported Languages

99 languages with auto-detection. Force with `-l <code>`:
`af, am, ar, as, az, ba, be, bg, bn, bo, br, bs, ca, cs, cy, da, de, el, en, eo, es, et, eu, fa, fi, fo, fr, fy, gd, gl, gu, ha, haw, he, hi, hr, ht, hu, hy, id, is, it, ja, jw, ka, kk, km, kn, ko, la, lb, ln, lo, lt, lv, mg, mi, mk, ml, mn, mr, ms, mt, my, ne, nl, nn, no, oc, pa, pl, ps, pt, ro, ru, sa, sd, si, sk, sl, sn, so, sq, sr, su, sv, sw, ta, te, tg, th, tk, tl, tr, tt, uk, ur, uz, vi, yi, yo, zh, zu`

## Edge Cases

- **yt-dlp extension mismatch**: yt-dlp may output `.mp4.webm` instead of `.mp4`. The CLI handles this by scanning the output directory for the most recent WAV file.
- **Large files (>1hr)**: Whisper processes in segments. Use `--model tiny` for speed on very long files.
- **Auto-detect language**: Detects from the first ~30 seconds. Specify `-l <code>` for multilingual audio where the primary language appears later.
- **No internet**: If transcribing a local file, use `--no-download` to skip yt-dlp entirely.
- **Authentication failures**: yt-dlp errors mentioning sign-in, private videos, bot checks or empty media responses come back with a remediation hint. Cookies are sent from Chrome by default — switch with `--browser firefox`, or disable with `--no-cookies` when the source is public and the cookie read fails.
- **Model not downloaded**: Run `vox init -m <model>` first, or models auto-download on first use.

## Supported File Formats

`.mp3, .mp4, .wav, .m4a, .flac, .ogg, .webm, .mkv, .avi, .mov, .aac, .wma, .opus, .ts`
