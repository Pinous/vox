import json as json_mod
import sys

import click

from vox.adapters.cli.open_hint import format_open_hint
from vox.adapters.cli.output_formatter import format_output
from vox.adapters.click_progress import ClickProgressReporter
from vox.adapters.disk_file_writer import DiskFileWriter
from vox.adapters.ffmpeg_audio_cleaner import FfmpegAudioCleaner
from vox.adapters.mlx_transcriber import MlxTranscriber
from vox.adapters.openai_transcriber import OpenAITranscriber
from vox.adapters.ytdlp_downloader import YtdlpDownloader
from vox.models.exceptions import VoxError
from vox.models.openai_model import OpenAIModel
from vox.models.transcription_backend import TranscriptionBackend
from vox.models.whisper_model import WhisperModel
from vox.ports.transcriber import Transcriber
from vox.use_cases.transcribe import TranscribeRequest, TranscribeUseCase


@click.command()
@click.argument("source", default="")
@click.option("-l", "--language", default="auto", help="ISO 639-1 code or 'auto'")
@click.option(
    "-m",
    "--model",
    default="small",
    help="tiny|base|small|medium|large-v3|large-v3-turbo",
)
@click.option("-o", "--output-dir", default=".", help="Output directory")
@click.option("-w", "--words", is_flag=True, help="Word-level timestamps")
@click.option("--fields", default=None, help="Comma-separated JSON fields")
@click.option("--dry-run", is_flag=True, help="Validate without executing")
@click.option("--format", "fmt", default=None, help="json|table")
@click.option("--no-clean", is_flag=True, help="Skip audio cleaning")
@click.option("--json", "json_payload", default=None, help="Raw JSON payload")
@click.option("--no-download", is_flag=True, help="Skip yt-dlp (local files only)")
@click.option(
    "-b",
    "--backend",
    default="local",
    help="local (MLX, default) | openai (cloud API)",
)
def transcribe(
    source,
    language,
    model,
    output_dir,
    words,
    fields,
    dry_run,
    fmt,
    no_clean,
    json_payload,
    no_download,
    backend,
):
    source, language, model = _apply_json_overrides(
        json_payload, source, language, model
    )
    try:
        backend_enum = TranscriptionBackend.from_string(backend)
        model = _resolve_model(model, backend_enum)
        _validate_model_for_backend(model, backend_enum)
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    use_case = _build_use_case(backend_enum)
    request = TranscribeRequest(
        source=source,
        language=language,
        model=model,
        output_dir=output_dir,
        word_timestamps=words,
        no_clean=no_clean,
        no_download=no_download,
        dry_run=dry_run,
    )
    try:
        response = use_case.execute(request)
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(format_output(response, fields, fmt))
    if _is_tty_mode(fmt) and not dry_run:
        click.echo(format_open_hint(response.srt_path), err=True)


def _is_tty_mode(fmt: str | None) -> bool:
    if fmt == "json":
        return False
    if fmt == "table":
        return True
    return sys.stdout.isatty()


def _apply_json_overrides(json_payload, source, language, model):
    if not json_payload:
        return source, language, model
    payload = json_mod.loads(json_payload)
    return (
        payload.get("input", source),
        payload.get("language", language),
        payload.get("model", model),
    )


def _build_use_case(backend: TranscriptionBackend) -> TranscribeUseCase:
    return TranscribeUseCase(
        downloader=YtdlpDownloader(),
        audio_cleaner=FfmpegAudioCleaner(),
        transcriber=_build_transcriber(backend),
        file_writer=DiskFileWriter(),
        progress=ClickProgressReporter(),
    )


def _build_transcriber(backend: TranscriptionBackend) -> Transcriber:
    if backend == TranscriptionBackend.OPENAI:
        return OpenAITranscriber()
    return MlxTranscriber()


def _validate_model_for_backend(model: str, backend: TranscriptionBackend) -> None:
    if backend == TranscriptionBackend.OPENAI:
        OpenAIModel.from_string(model)
    else:
        WhisperModel.from_string(model)


def _resolve_model(model: str, backend: TranscriptionBackend) -> str:
    if backend == TranscriptionBackend.OPENAI and model == "small":
        return "gpt-4o-transcribe"
    return model
