import shutil
import sys

import click

from vox.adapters.cli.output_formatter import format_output
from vox.adapters.click_progress import ClickProgressReporter
from vox.adapters.disk_file_cleaner import DiskFileCleaner
from vox.adapters.disk_file_writer import DiskFileWriter
from vox.adapters.disk_metadata_writer import DiskMetadataWriter
from vox.adapters.ffmpeg_audio_cleaner import FfmpegAudioCleaner
from vox.adapters.mlx_transcriber import MlxTranscriber
from vox.adapters.noop_summarizer import NoopSummarizer
from vox.adapters.rclone_uploader import RcloneUploader
from vox.adapters.ytdlp_channel_lister import YtdlpChannelLister
from vox.adapters.ytdlp_downloader import YtdlpDownloader
from vox.models.exceptions import VoxError
from vox.use_cases.batch_transcribe import (
    BatchTranscribeRequest,
    BatchTranscribeUseCase,
)
from vox.use_cases.transcribe import TranscribeUseCase


@click.command()
@click.argument("url")
@click.option(
    "--years",
    required=True,
    help="Comma-separated years (e.g. 2025,2026)",
)
@click.option("-l", "--language", default="auto")
@click.option("-m", "--model", default="small")
@click.option("-o", "--output-dir", default=".")
@click.option("--no-clean", is_flag=True)
@click.option("--upload", is_flag=True, help="Upload via rclone")
@click.option("--remote", default="", help="rclone remote name")
@click.option("--remote-folder", default="")
@click.option("--no-cleanup", is_flag=True, help="Keep audio files")
@click.option("--no-cookies", is_flag=True, help="Don't use browser cookies")
@click.option("--sleep", default=1, help="Seconds between requests")
@click.option("--dry-run", is_flag=True)
@click.option("--limit", default=0, help="Max videos to process (0=all)")
@click.option("--format", "fmt", default=None, help="json|table")
@click.option(
    "--summarizer",
    default="auto",
    help="auto|claude|anthropic|none",
)
def channel(
    url,
    years,
    language,
    model,
    output_dir,
    no_clean,
    upload,
    remote,
    remote_folder,
    no_cleanup,
    no_cookies,
    sleep,
    dry_run,
    limit,
    fmt,
    summarizer,
):
    parsed_years = _parse_years(years)
    use_cookies = not no_cookies
    use_case = _build_use_case(summarizer, use_cookies, sleep)
    request = BatchTranscribeRequest(
        channel_url=url,
        years=parsed_years,
        language=language,
        model=model,
        output_dir=output_dir,
        no_clean=no_clean,
        upload=upload,
        remote_name=remote,
        remote_folder=remote_folder,
        cleanup=not no_cleanup,
        dry_run=dry_run,
        limit=limit,
    )
    try:
        result = use_case.execute(request)
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(format_output(result, None, fmt))


def _parse_years(raw: str) -> tuple[int, ...]:
    return tuple(int(y.strip()) for y in raw.split(","))


def _build_summarizer(choice: str):
    if choice == "none":
        return NoopSummarizer()
    if choice == "anthropic":
        return _anthropic_summarizer()
    if choice == "claude":
        return _claude_summarizer()
    return _auto_summarizer()


def _auto_summarizer():
    if shutil.which("claude"):
        return _claude_summarizer()
    return NoopSummarizer()


def _claude_summarizer():
    from vox.adapters.claude_summarizer import ClaudeSummarizer

    return ClaudeSummarizer()


def _anthropic_summarizer():
    from vox.adapters.anthropic_summarizer import AnthropicSummarizer

    return AnthropicSummarizer()


def _build_use_case(
    summarizer_choice: str,
    use_cookies: bool,
    sleep_interval: int,
) -> BatchTranscribeUseCase:
    progress = ClickProgressReporter()
    downloader = YtdlpDownloader(use_cookies=use_cookies)
    transcribe = TranscribeUseCase(
        downloader=downloader,
        audio_cleaner=FfmpegAudioCleaner(),
        transcriber=MlxTranscriber(),
        file_writer=DiskFileWriter(),
        progress=progress,
    )
    return BatchTranscribeUseCase(
        channel_lister=YtdlpChannelLister(
            use_cookies=use_cookies,
            sleep_interval=sleep_interval,
        ),
        transcribe=transcribe,
        file_uploader=RcloneUploader(),
        file_cleaner=DiskFileCleaner(),
        progress=progress,
        summarizer=_build_summarizer(summarizer_choice),
        metadata_writer=DiskMetadataWriter(),
    )
