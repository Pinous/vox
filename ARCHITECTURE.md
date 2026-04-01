# vox — Architecture Guide

> A Python CLI for audio/video transcription using MLX Whisper on Apple Silicon.
> Rewritten from the TypeScript `trx` tool (https://github.com/crafter-station/trx).

---

## What Does vox Do?

You hand it a local audio file or a YouTube URL. It downloads the audio (if needed),
cleans it up, runs it through OpenAI's Whisper model on your Mac's GPU/Neural Engine,
and spits out three files: `.srt` (subtitles), `.txt` (plain text), `.json` (full
structured data with timestamps).

```
$ vox recording.mp3
$ vox https://youtube.com/watch?v=...
$ vox audio.wav --language fr --model large-v3
```

The whole pipeline in one sentence: URL or file in, transcript files out.

---

## The Big Picture: Hexagonal Architecture

Imagine a fortress. The core of the fortress — the keep — holds all your business
rules. Around it are walls (ports). Outside the walls are the real world adapters:
CLI, ffmpeg, yt-dlp, mlx-whisper. The keep doesn't know anything about what's outside
the walls. It only knows about the shapes of the gates (ports).

This is Hexagonal Architecture (also called Ports and Adapters). The payoff: you can
swap anything outside the walls — replace mlx-whisper with OpenAI's API, replace
yt-dlp with a different downloader — without touching a single line of business logic.
And you can test the keep in total isolation, with fake gates that do nothing.

```
                  ┌─────────────────────────────────┐
                  │           CORE (Keep)            │
                  │                                  │
 CLI (Click)  ──► │  use_cases/   models/            │
                  │  TranscribeUseCase               │
 Agent (pipe) ──► │  CheckHealthUseCase              │
                  │  InitDepsUseCase                 │
                  │                                  │
                  │  ports/ (interfaces)             │
                  │  Transcriber  Downloader         │
                  │  AudioCleaner FileWriter         │
                  └──────────┬──────────────────────┘
                             │
          ┌──────────────────┼──────────────────────┐
          │                  │                      │
   MlxTranscriber   FfmpegAudioCleaner    YtdlpDownloader
   (mlx-whisper)    (ffmpeg subprocess)  (yt-dlp subprocess)
```

**Key principle:** The core imports nothing from adapters. Adapters import from the
core. Dependency arrows always point inward.

---

## Directory Structure

```
src/vox/
  models/          # Pure data: frozen dataclasses, enums, validation
  ports/           # Interfaces: Python Protocols (no implementation)
  use_cases/       # Business logic: orchestrates ports, no I/O
  adapters/
    cli/           # Click commands (primary adapter — drives the app)
    mlx_transcriber.py     # calls mlx-whisper library
    ffmpeg_audio_cleaner.py # shells out to ffmpeg
    ytdlp_downloader.py    # shells out to yt-dlp
```

---

## The Transcription Pipeline, Step by Step

`TranscribeUseCase.execute()` is the heart of the app. Here is what happens:

1. **Validate input** — `TranscriptionInput.from_string()` checks the source string:
   is it a URL or a file path? Does it have a supported extension? Is there a path
   traversal attempt (`..`)? Fail fast, before touching any I/O.

2. **Validate language and model** — `Language.from_string()` and
   `WhisperModel.from_string()` parse and validate user input into typed value objects.
   Unknown model name? You get a `ValidationError` immediately, not a cryptic crash
   10 seconds later.

3. **Download (if URL)** — `Downloader.download()` is called only when the source is
   a URL. `YtdlpDownloader` shells out to `yt-dlp -x --audio-format wav`.

4. **Clean audio** — `AudioCleaner.clean()` calls `FfmpegAudioCleaner`, which builds
   an ffmpeg filter chain: silence removal, FFT denoising, dynamic normalization.
   Whisper works significantly better on clean, normalized 16kHz mono WAV files.
   Use `--no-clean` to skip this step.

5. **Transcribe** — `Transcriber.transcribe()` calls `MlxTranscriber`, which calls
   `mlx_whisper.transcribe()` — the Python library, not a subprocess. MLX runs the
   model directly on Apple Silicon's unified memory (GPU + Neural Engine).

6. **Write outputs** — Three files: `.srt`, `.txt`, `.json`. Each written via the
   `FileWriter` port to keep I/O isolated.

7. **Return a `TranscribeResponse`** — A frozen dataclass with `text`, `language`,
   and the three output file paths. The CLI then formats and prints it.

---

## The Models Layer: Frozen Dataclasses as Value Objects

Every model in `src/vox/models/` is a `@dataclass(frozen=True)`. This is not a style
choice — it is a deliberate design constraint.

Frozen dataclasses are immutable. Once created, they cannot be mutated. This eliminates
an entire class of bugs: no one can sneak in and change a `TranscribeRequest` halfway
through execution. Functions that receive a `TranscribeRequest` can trust it will not
change under their feet.

```python
@dataclass(frozen=True)
class TranscribeRequest:
    source: str
    language: str = "auto"
    model: str = "small"
    ...
```

`Segment` goes further: it validates in `__post_init__` that `end > start`. You cannot
even construct an invalid `Segment`. The constructor is the validation boundary.

`WhisperModel` is an `Enum` whose values are HuggingFace repo identifiers:

```python
class WhisperModel(Enum):
    SMALL = "mlx-community/whisper-small-mlx"
    LARGE_V3 = "mlx-community/whisper-large-v3-mlx"
    ...
```

The model name the user types (`"small"`) maps directly to the HuggingFace repo
(`"mlx-community/whisper-small-mlx"`) with zero magic strings elsewhere in the code.

---

## The Ports Layer: Python Protocols as Interfaces

Ports are defined using Python's `typing.Protocol`. A Protocol is a structural
interface — any class that has the right methods satisfies it, without needing to
inherit from anything.

```python
class Transcriber(Protocol):
    def transcribe(
        self,
        audio_path: Path,
        model: WhisperModel,
        language: str | None,
        word_timestamps: bool,
    ) -> TranscriptionResult: ...
```

`MlxTranscriber` satisfies this Protocol because it has that method signature. So does
`FakeTranscriber` in the tests. Neither inherits from `Transcriber`. Python checks
structural compatibility — duck typing with type-checker support.

This is the mechanism that makes the hexagon work: the use case depends on the
`Transcriber` Protocol (an abstraction), not on `MlxTranscriber` (a concrete class).

---

## The CLI Layer: Click and the Default Command Trick

The CLI uses [Click](https://click.palletsprojects.com/). There are four commands:
`transcribe`, `init`, `doctor`, `schema`.

There is one non-obvious trick: `vox audio.mp3` should work without typing `transcribe`.
Click's `Group` normally requires a subcommand name. The solution is a custom group
class:

```python
class DefaultTranscribeGroup(click.Group):
    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = ["transcribe", *args]
        return super().parse_args(ctx, args)
```

If the first argument is not a known command name and not a flag, prepend `"transcribe"`
to the args list. This intercepts parsing before Click processes anything. The gotcha:
this check happens at parse time, so it must be cheap and correct — a bad check here
breaks all CLI argument parsing.

### Agent Mode: TTY Detection

vox is "agent-first": it behaves differently when piped versus when used interactively.
The `output_formatter.py` detects `sys.stdout.isatty()`:

- TTY (human terminal) → table format, human-readable
- No TTY (pipe, agent) → JSON, machine-parseable

This means `vox transcribe audio.mp3 | jq .text` just works. No flags needed. The
`doctor` command also exits with code 1 if any dependency is missing — agents can
check health with a simple exit code test.

---

## Technology Choices — and Why

### MLX Whisper (not whisper.cpp, not OpenAI API)

Three options existed for running Whisper on Mac:
1. `whisper.cpp` — C++ binary, excellent performance, but requires subprocess and
   careful binary management.
2. OpenAI API — network required, costs money per minute, no offline use.
3. `mlx-whisper` — Python library, runs on Apple Silicon via the MLX framework
   (Apple's ML framework for M-series chips). Uses unified memory across CPU, GPU, and
   Neural Engine.

`mlx-whisper` wins because it is a Python library import, not a subprocess call. This
means: no binary path management, no version mismatches, errors come back as Python
exceptions (not stderr strings to parse), and the integration is a single function
call: `mlx_whisper.transcribe(str(audio_path), **kwargs)`.

The gotcha that bit us: `mlx-whisper` is imported as `mlx_whisper` (underscore, not
hyphen). The package name and the import name differ. Common Python packaging pattern,
but worth knowing before you spend time debugging an `ImportError`.

### ffmpeg via subprocess (not a Python library)

ffmpeg is the industry standard for audio/video processing. The Python bindings
(`ffmpeg-python`) add a layer of abstraction that can obscure errors. Calling ffmpeg
directly with `subprocess.run()` gives exact control over the command and makes the
filter chain (`-af`) readable and auditable. The tradeoff is that ffmpeg must be
installed separately — hence `vox doctor` to check for it.

### yt-dlp via subprocess

Same rationale. `yt-dlp` has no stable Python library interface — it is designed to be
used as a CLI tool. The adapter parses stdout to find the downloaded file path, with a
fallback to "find the most recently modified .wav in the output directory." Fragile?
Slightly. But yt-dlp's stdout format is stable and well-documented.

### uv for package management

[uv](https://github.com/astral-sh/uv) replaces pip + virtualenv + pip-tools. It is
written in Rust and resolves/installs dependencies in milliseconds, not seconds. The
`pyproject.toml` is the single source of truth. `uv sync` is the only command needed
to set up a fresh environment.

---

## TDD and the Fake Strategy

The test suite tests `TranscribeUseCase` without ever touching the filesystem, network,
or GPU. Here is how: every port has a corresponding `Fake*` class in `tests/fakes/`.

```python
class FakeTranscriber:
    def __init__(self, result=None):
        self._result = result or _default_result()
        self.transcribe_called_with: tuple | None = None

    def transcribe(self, audio_path, model, language, word_timestamps):
        self.transcribe_called_with = (audio_path, model, language, word_timestamps)
        return self._result
```

The fake records what it was called with (for assertion), and returns a predictable
result. No GPU. No network. No disk. Test runs in milliseconds.

The `TranscribeFixture` class wires all the fakes together:

```python
class TranscribeFixture:
    def __init__(self):
        self.downloader = FakeDownloader()
        self.transcriber = FakeTranscriber()
        ...
        self.use_case = TranscribeUseCase(
            downloader=self.downloader,
            transcriber=self.transcriber, ...
        )
```

Each test creates a `TranscribeFixture`, calls `fix.execute(...)`, and asserts on the
fakes' recorded state. This is the payoff of hexagonal architecture: the seams are
real, and you can inject anything through them.

Tests are marked with pytest markers so integration tests (which need real binaries)
can be skipped in fast CI runs:

```ini
[tool.pytest.ini_options]
markers = [
    "integration: requires external tools (yt-dlp, ffmpeg, mlx-whisper)",
    "e2e: end-to-end CLI tests",
]
```

---

## Error Handling: A Hierarchy of Failures

All errors inherit from `VoxError`. The CLI catches `VoxError` and prints to stderr
with exit code 1. Nothing else leaks to the user.

```
VoxError
  ValidationError    — bad input (wrong file extension, unknown language)
  DependencyError    — missing binary (ffmpeg not installed)
  DownloadError      — yt-dlp failed
  AudioCleaningError — ffmpeg returned non-zero
  TranscriptionError — mlx-whisper raised an exception
  ConfigError        — .vox config file unreadable
```

This hierarchy means callers can catch at any level of specificity. A CLI that only
wants to show a generic error catches `VoxError`. An integration test that wants to
assert "this raises when ffmpeg is missing" catches `DependencyError`.

---

## The `schema` Command: Agent Introspection

`vox schema transcribe` outputs a JSON schema describing the `transcribe` command's
inputs and outputs. This exists for AI agents: an agent can call `vox schema transcribe`
at runtime to discover what fields are available, what models are supported, and what
the response shape looks like — without reading source code.

This is what "agent-first" means architecturally: the CLI is designed to be consumed
by both humans and automated systems. TTY detection handles formatting. The schema
command handles discovery.

---

## Lessons Learned and Gotchas

**Click's default command ambiguity.** Click does not natively support "run a default
subcommand when no subcommand is given." The `DefaultTranscribeGroup` trick works, but
it intercepts raw args before Click processes them. If you add a new top-level flag
(e.g., `--version`), you must ensure the check `not args[0].startswith("-")` still
holds. Flags starting with `-` are correctly excluded; positional arguments that happen
to match a future command name are not.

**mlx-whisper is a library, not a binary.** The original TypeScript `trx` tool called
whisper as a subprocess. `vox` imports it as a Python library. This is cleaner, but it
means `mlx-whisper` must be in the same Python environment as `vox`. If you install
`vox` globally and `mlx-whisper` in a venv, you will get `ImportError`. The fix: always
install everything in the same environment with `uv sync`.

**Frozen dataclasses and `tuple` for collections.** `TranscriptionResult.segments` is
typed as `tuple[Segment, ...]`, not `list[Segment]`. This is intentional: lists are
mutable, tuples are not. A frozen dataclass containing a list is not truly immutable —
you can still mutate the list. Tuples close that loophole.

**yt-dlp stdout parsing is fragile but necessary.** yt-dlp does not return the output
file path via a stable API. The adapter parses stdout looking for lines containing
`Destination:`. If that fails, it falls back to "most recently modified .wav file."
This works in practice but means the adapter has implicit coupling to yt-dlp's output
format. If yt-dlp changes its log format, the adapter needs updating. The integration
tests catch this.

**ffmpeg filter order matters.** Silence removal should happen before denoising, and
denoising before normalization. The filter chain is order-sensitive: `silenceremove`,
then `afftdn` (FFT denoiser), then `dynaudnorm`. Getting this wrong produces audio
artifacts that confuse Whisper.

**Protocols don't enforce — they guide.** Python's `typing.Protocol` is not enforced
at runtime unless you use `isinstance()` with `runtime_checkable`. The fakes work
because they structurally match the Protocol. But a fake with a wrong signature
compiles fine and only fails when called. This is why the fakes are tested implicitly
through the use case tests — if a fake has the wrong shape, the use case test will fail.

---

## Reading Guide

- Start with `src/vox/use_cases/transcribe.py` to understand the business logic.
- Then read `src/vox/ports/` to understand the abstractions.
- Then read `tests/unit/use_cases/test_transcribe.py` to see the TDD style.
- Then read `src/vox/adapters/mlx_transcriber.py` to see how a real adapter works.
- Finally, read `src/vox/adapters/cli/app.py` and `transcribe_cmd.py` to see how the
  CLI wires everything together.

The CLI is the last thing to read because it is the least interesting architecturally.
Its job is construction and delegation, nothing more.
