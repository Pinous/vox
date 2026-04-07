# ADR-002: OpenAI cloud backend as opt-in alternative to local MLX

**Date**: 2026-04-07
**Status**: Accepted

## Context

`vox` was Apple-Silicon-only by design — it wraps `mlx-whisper`, which
only runs on Metal. That excluded every Linux and Windows user, plus
anyone who wanted to transcribe a file too large to fit in local
memory or who simply wanted faster cloud transcription.

The reference project `crafter-station/trx` had just shipped a
`--backend openai` flag in v0.4.0 that solved exactly this problem:
keep the local backend as default, add OpenAI as an escape hatch for
non-Apple-Silicon users and large files.

The challenge for `vox`: do this without polluting the existing
positioning ("local-first, no cloud, no API key, no cost per minute")
and without forcing every user to install the `openai` Python package.

## Decisions

### OpenAI is opt-in, never the default

The default backend stays `local`. Users explicitly pass `-b openai`
to opt in. The README still leads with the local-first pitch — the
OpenAI backend is documented as a fallback, not a feature parity with
the local path.

Why: the project's identity is local-first transcription. The OpenAI
backend serves a different audience (cross-platform, large files) but
should not dilute the core message.

### `vox channel` does NOT get a `--backend` flag

Even though the architecture supports it cleanly, `vox channel` is
deliberately excluded from backend selection. YouTube videos are
typically much larger than the OpenAI 25 MB API limit, so allowing
`-b openai` on `vox channel` would create a footgun where every batch
run fails on the first long video.

Users who want cloud transcription on a single YouTube video can
still download manually and run `vox transcribe -b openai`.

### Refactor: `Transcriber` port now accepts `model: str`

Before: the port signature was `model: WhisperModel`. The use case
called `WhisperModel.from_string()` and passed the enum to the
adapter. This worked for one backend but coupled the port to a
specific model type.

After: the port accepts `model: str`. Each adapter resolves the
string into its own enum:

- `MlxTranscriber` calls `WhisperModel.from_string(model)`
- `OpenAITranscriber` calls `OpenAIModel.from_string(model)`

The use case is now backend-agnostic. Validation moved to the CLI
builder, where the right enum is picked based on `--backend`. Dry-run
still validates the model upfront because the CLI builder runs before
the use case.

Why this refactor: keeping `WhisperModel` in the port signature would
have forced an awkward `Union[WhisperModel, OpenAIModel]` or a base
class hierarchy. Passing a `str` is the loosest contract that lets
each adapter own its own model knowledge. SRP wins.

### OpenAI SDK as lazy import, not a project dependency

The `openai` package is imported lazily inside
`OpenAITranscriber._default_api_caller()`. It is not declared in
`pyproject.toml`. If the user runs `-b openai` without installing the
SDK, they get a clear error: `openai package not installed. Run: uv
add openai`.

Why: matches the existing pattern from `AnthropicSummarizer` (which
also lazy-imports `anthropic`). Keeps the default install lightweight
for the local-only majority of users.

### Inject `api_caller` and `duration_probe` for testability

The adapter constructor takes two optional callables:

```python
class OpenAITranscriber:
    def __init__(self, api_caller=None, duration_probe=None):
        self._api_caller = api_caller or _default_api_caller
        self._duration_probe = duration_probe or _ffprobe_duration
```

Tests inject fakes — no real HTTP, no `ffprobe` requirement. The
default callers do the real work in production.

Why: hexagonal purity. Mocking `urllib` or patching the OpenAI SDK
inside tests would couple the test suite to implementation details.
Constructor injection keeps the unit tests fast and deterministic.

### 25 MB file size validation, upfront

The OpenAI Audio API rejects files larger than 25 MB. The adapter
checks `audio_path.stat().st_size` before making the network call and
raises a `ValidationError` with a clear redirect:

```
file is 47.2 MB — OpenAI API limit is 25 MB.
Use --backend local for large files.
```

Why: failing fast at the boundary is cheaper than letting the API
return a 413, and the error message tells the user exactly how to
recover.

### Word-level timestamps not supported on OpenAI

Passing `--words` together with `-b openai` raises a
`ValidationError` immediately. The OpenAI Whisper-1 API supports word
granularity, but `gpt-4o-transcribe` and `gpt-4o-mini-transcribe` do
not. Rather than silently degrading on the gpt-4o models, the adapter
rejects all word-level requests.

Why: consistent UX. A user who asks for `--words` should never get a
result without timestamps and not know it.

### Auto-resolve default model when switching backends

The default model is `small` (a local Whisper model). If the user
passes `-b openai` without `-m`, the CLI silently substitutes the
OpenAI default `gpt-4o-transcribe` instead of failing validation.

```python
def _resolve_model(model: str, backend: TranscriptionBackend) -> str:
    if backend == TranscriptionBackend.OPENAI and model == "small":
        return "gpt-4o-transcribe"
    return model
```

This is the only piece of "magic" in the CLI — every other case
preserves the user's explicit input. Users who want a different
OpenAI model still pass `-m gpt-4o-mini-transcribe`.

Why: zero-friction default. `vox transcribe podcast.mp3 -b openai`
should just work, without forcing the user to remember the OpenAI
model name.

### `large-v3-turbo` added to local models

Added as a new member of `WhisperModel` with the alias `large-v3-turbo`.
Newer Whisper variant — faster than `large-v3` with near-identical
quality. mlx-whisper supports it out of the box.

### `vox doctor` reports OpenAI status

The `HealthReport` gains an `openai_api_key_set: bool` field. The
doctor command shows it in both JSON and table output:

```
OpenAI API key: set
```

Why: when something goes wrong with `-b openai`, the user wants to
check that the env var is exported without leaving the CLI. `vox
doctor` is the natural place.

### Platform-aware install hints

When `vox doctor` reports a missing dependency, it now suggests an
install command based on `sys.platform`:

| Dependency      | macOS                | Linux                       | Windows                  |
| --------------- | -------------------- | --------------------------- | ------------------------ |
| `ffmpeg`        | `brew install ffmpeg`| `sudo apt install ffmpeg`   | `winget install ffmpeg`  |
| `yt-dlp`        | `brew install yt-dlp`| `sudo apt install yt-dlp`   | `winget install yt-dlp`  |
| `mlx-whisper`   | `uv add mlx-whisper` | "Apple Silicon only — use --backend openai elsewhere" | (same)             |

Why: the OpenAI backend opens the door to Linux and Windows users.
The doctor must speak their package manager too.

### Open hint after successful transcription

In TTY mode, `vox transcribe` prints a final hint:

```
-> open /tmp/audio.srt
```

Suppressed in JSON / agent mode (would pollute the structured
output). Paths are quoted with `shlex.quote` so titles with spaces or
apostrophes copy-paste correctly.

Why: small UX touch borrowed from `trx`. Saves the user the cd /
copy / paste cycle.

## Architecture

```
Models (inner layer)
  + OpenAIModel (gpt-4o-transcribe, gpt-4o-mini-transcribe, whisper-1)
  + TranscriptionBackend (LOCAL, OPENAI)
  + WhisperModel.LARGE_V3_TURBO

Ports
  Transcriber.transcribe(audio_path, model: str, language, word_timestamps)
  ^ refactored: model is now str, not WhisperModel

Adapters
  MlxTranscriber       — resolves model via WhisperModel.from_string
  OpenAITranscriber    — resolves model via OpenAIModel.from_string
                         injects api_caller + duration_probe
  CLI install_hints    — pure function: (dep, platform) -> str
  CLI open_hint        — pure function: (path) -> str via shlex.quote

Use case
  TranscribeUseCase    — backend-agnostic, no longer validates model
                         (validation moved to CLI builder)

CLI
  vox transcribe -b openai|local -m <model>
    ├── _validate_model_for_backend (uses the right enum)
    ├── _resolve_model (auto-substitutes default for OpenAI)
    └── _build_transcriber (picks adapter)
  vox doctor — shows openai_api_key_set + per-platform install hints
```

## Files created

| File                                          | Purpose                                       |
| --------------------------------------------- | --------------------------------------------- |
| `src/vox/models/openai_model.py`              | `OpenAIModel` enum (3 models, segment support)|
| `src/vox/models/transcription_backend.py`     | `TranscriptionBackend` enum (LOCAL, OPENAI)   |
| `src/vox/adapters/openai_transcriber.py`      | OpenAI adapter, lazy SDK, injectable callers  |
| `src/vox/adapters/cli/open_hint.py`           | `format_open_hint(path)` with shell quoting   |
| `src/vox/adapters/cli/install_hints.py`       | `format_install_hint(dep, platform)`          |
| `tests/unit/models/test_openai_model.py`      | 8 tests                                       |
| `tests/unit/models/test_transcription_backend.py` | 4 tests                                   |
| `tests/unit/adapters/test_openai_transcriber.py`  | 8 tests with FakeApiCaller                |
| `tests/unit/adapters/test_open_hint.py`       | 3 tests for shell quoting                     |
| `tests/unit/adapters/test_install_hints.py`   | 10 tests for cross-platform commands          |

## Files modified

| File                                       | Change                                          |
| ------------------------------------------ | ----------------------------------------------- |
| `src/vox/ports/transcriber.py`             | `model: WhisperModel` → `model: str`            |
| `src/vox/adapters/mlx_transcriber.py`      | Resolves model string internally                |
| `src/vox/use_cases/transcribe.py`          | Removed `WhisperModel.from_string` call         |
| `src/vox/use_cases/check_health.py`        | +`openai_api_key_set` on `HealthReport`         |
| `src/vox/adapters/cli/transcribe_cmd.py`   | +`-b/--backend` flag, validation, model resolution |
| `src/vox/adapters/cli/doctor_cmd.py`       | Display OpenAI key + platform install hints     |
| `src/vox/models/whisper_model.py`          | +`LARGE_V3_TURBO`                               |
| `tests/fakes/fake_transcriber.py`          | Signature: `model: WhisperModel` → `model: str` |
| `tests/unit/use_cases/test_check_health.py`| +2 tests for OpenAI key detection               |
| `tests/unit/models/test_whisper_model.py`  | +3 tests for `LARGE_V3_TURBO`                   |
| `README.md` and `skills/vox/SKILL.md`      | Document `-b openai`, OpenAI model table, examples |

## Consequences

- `vox transcribe -b openai` works on any OS where Python runs, not
  just Apple Silicon
- The default user experience is unchanged: `vox file.mp3` still uses
  the local MLX backend with the `small` model
- The 25 MB limit is enforced before the network call, with a clear
  redirect to `--backend local`
- `--words` rejects the OpenAI backend immediately — no silent
  degradation
- The `Transcriber` port can now host any future transcription
  backend (Deepgram, AssemblyAI, etc.) by adding an adapter — no
  changes needed in the use case
- The lazy import of the `openai` SDK keeps the default install
  lightweight; only users who actually want the OpenAI backend pay
  the dependency cost
- `vox doctor` is now useful on Linux and Windows: it tells you which
  package manager to use, and reports whether your OpenAI key is set
- Total test count: 107 → 145 (+38), all using fakes / injected
  callers, no real network or filesystem dependency
