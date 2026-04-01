import json as json_mod
import sys

import click

from vox.adapters.cli.output_formatter import format_output
from vox.adapters.click_progress import ClickProgressReporter
from vox.adapters.disk_file_writer import DiskFileWriter
from vox.adapters.ffmpeg_audio_cleaner import FfmpegAudioCleaner
from vox.adapters.mlx_transcriber import MlxTranscriber
from vox.adapters.ytdlp_downloader import YtdlpDownloader
from vox.models.exceptions import VoxError
from vox.use_cases.transcribe import TranscribeRequest, TranscribeUseCase


@click.command()
@click.argument("source", default="")
@click.option("-l", "--language", default="auto", help="ISO 639-1 code or 'auto'")
@click.option("-m", "--model", default="small", help="tiny|base|small|medium|large-v3")
@click.option("-o", "--output-dir", default=".", help="Output directory")
@click.option("-w", "--words", is_flag=True, help="Word-level timestamps")
@click.option("--fields", default=None, help="Comma-separated JSON fields")
@click.option("--dry-run", is_flag=True, help="Validate without executing")
@click.option("--format", "fmt", default=None, help="json|table")
@click.option("--no-clean", is_flag=True, help="Skip audio cleaning")
@click.option("--json", "json_payload", default=None, help="Raw JSON payload")
@click.option("--no-download", is_flag=True, help="Skip yt-dlp (local files only)")
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
):
    source, language, model = _apply_json_overrides(
        json_payload, source, language, model
    )
    use_case = _build_use_case()
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


def _apply_json_overrides(json_payload, source, language, model):
    if not json_payload:
        return source, language, model
    payload = json_mod.loads(json_payload)
    return (
        payload.get("input", source),
        payload.get("language", language),
        payload.get("model", model),
    )


def _build_use_case() -> TranscribeUseCase:
    return TranscribeUseCase(
        downloader=YtdlpDownloader(),
        audio_cleaner=FfmpegAudioCleaner(),
        transcriber=MlxTranscriber(),
        file_writer=DiskFileWriter(),
        progress=ClickProgressReporter(),
    )
