from __future__ import annotations

import contextlib
import re
from dataclasses import dataclass
from pathlib import Path

from vox.models.batch_result import BatchItemResult, BatchResult
from vox.models.channel_video import ChannelVideo
from vox.models.date_range import DateRange
from vox.models.exceptions import VoxError
from vox.models.video_metadata import VideoMetadata
from vox.ports.channel_lister import ChannelLister
from vox.ports.file_cleaner import FileCleaner
from vox.ports.file_uploader import FileUploader
from vox.ports.metadata_writer import MetadataWriter
from vox.ports.progress_reporter import ProgressReporter
from vox.ports.transcript_summarizer import TranscriptSummarizer
from vox.use_cases.transcribe import (
    TranscribeRequest,
    TranscribeResponse,
    TranscribeUseCase,
)


@dataclass(frozen=True)
class BatchTranscribeRequest:
    channel_url: str
    years: tuple[int, ...]
    language: str = "auto"
    model: str = "small"
    output_dir: str = "."
    no_clean: bool = False
    upload: bool = False
    remote_name: str = ""
    remote_folder: str = ""
    cleanup: bool = True
    dry_run: bool = False
    limit: int = 0


class BatchTranscribeUseCase:
    def __init__(
        self,
        channel_lister: ChannelLister,
        transcribe: TranscribeUseCase,
        file_uploader: FileUploader,
        file_cleaner: FileCleaner,
        progress: ProgressReporter,
        summarizer: TranscriptSummarizer,
        metadata_writer: MetadataWriter,
    ):
        self._channel_lister = channel_lister
        self._transcribe = transcribe
        self._file_uploader = file_uploader
        self._file_cleaner = file_cleaner
        self._progress = progress
        self._summarizer = summarizer
        self._metadata_writer = metadata_writer

    def execute(self, request: BatchTranscribeRequest) -> BatchResult:
        date_range = DateRange.from_years(request.years)
        self._progress.start("Listing channel videos")
        videos = self._channel_lister.list_videos(request.channel_url, date_range)
        if request.limit > 0:
            videos = videos[: request.limit]
        if request.dry_run:
            return _dry_run_result(videos)
        items, all_meta = self._process_videos(videos, request)
        output_dir = Path(request.output_dir)
        self._metadata_writer.write_index(tuple(all_meta), output_dir)
        self._metadata_writer.write_claude_md(output_dir)
        self._try_upload_root(output_dir, request)
        return _build_result(items)

    def _try_upload_root(
        self,
        output_dir: Path,
        request: BatchTranscribeRequest,
    ) -> None:
        if not request.upload:
            return
        remote_root = f"{request.remote_name}:{request.remote_folder}"
        for name in ("index.md", "CLAUDE.md"):
            path = output_dir / name
            if path.exists():
                with contextlib.suppress(VoxError):
                    self._file_uploader.upload(path, remote_root)

    def _process_videos(
        self,
        videos: tuple[ChannelVideo, ...],
        request: BatchTranscribeRequest,
    ) -> tuple[list[BatchItemResult], list[VideoMetadata]]:
        items: list[BatchItemResult] = []
        all_meta: list[VideoMetadata] = []
        for i, video in enumerate(videos, 1):
            self._progress.update(f"[{i}/{len(videos)}] {video.title}")
            item, meta = self._process_one(video, request)
            items.append(item)
            if meta:
                all_meta.append(meta)
        return items, all_meta

    def _process_one(
        self,
        video: ChannelVideo,
        request: BatchTranscribeRequest,
    ) -> tuple[BatchItemResult, VideoMetadata | None]:
        try:
            folder = _video_folder(Path(request.output_dir), video)
            response = self._transcribe_video(video, request, folder)
            meta = self._enrich_and_write_meta(video, response, folder)
        except Exception as e:
            return _failure_item(video, str(e)), None
        self._try_upload(response, video, folder, request)
        self._maybe_cleanup(response, folder, request)
        return _success_item(video, response), meta

    def _transcribe_video(
        self,
        video: ChannelVideo,
        request: BatchTranscribeRequest,
        folder: Path,
    ) -> TranscribeResponse:
        transcribe_request = TranscribeRequest(
            source=video.url,
            language=request.language,
            model=request.model,
            output_dir=str(folder),
            no_clean=request.no_clean,
            output_stem="transcript",
        )
        return self._transcribe.execute(transcribe_request)

    def _enrich_and_write_meta(
        self,
        video: ChannelVideo,
        response: TranscribeResponse,
        folder: Path,
    ) -> VideoMetadata:
        summary_result = self._summarizer.summarize(response.text, video.title)
        meta = VideoMetadata(
            title=video.title,
            url=video.url,
            author=video.channel_name,
            date=_format_date(video.upload_date),
            duration=_format_duration(video.duration_seconds),
            language=response.language,
            topics=summary_result.topics,
            summary=summary_result.summary,
            folder_name=_folder_name(video),
        )
        self._metadata_writer.write_meta(meta, folder)
        return meta

    def _try_upload(
        self,
        response: TranscribeResponse,
        video: ChannelVideo,
        folder: Path,
        request: BatchTranscribeRequest,
    ) -> None:
        if not request.upload:
            return
        try:
            self._do_upload(response, video, folder, request)
        except VoxError:
            self._progress.update(f"Upload failed for {video.title}")

    def _do_upload(
        self,
        response: TranscribeResponse,
        video: ChannelVideo,
        folder: Path,
        request: BatchTranscribeRequest,
    ) -> None:
        remote = _build_remote_folder(
            request.remote_name,
            request.remote_folder,
            video.channel_name,
            video,
        )
        for path_str in (
            response.srt_path,
            response.txt_path,
            response.json_path,
        ):
            self._file_uploader.upload(Path(path_str), remote)
        meta_path = folder / "meta.md"
        if meta_path.exists():
            self._file_uploader.upload(meta_path, remote)

    def _maybe_cleanup(
        self,
        response: TranscribeResponse,
        folder: Path,
        request: BatchTranscribeRequest,
    ) -> None:
        if not request.cleanup:
            return
        for wav in folder.glob("*.wav"):
            self._file_cleaner.delete(wav)


def _folder_name(video: ChannelVideo) -> str:
    date = _format_date(video.upload_date)
    slug = _slugify(video.title)
    return f"{date}_{slug}"


def _video_folder(output_dir: Path, video: ChannelVideo) -> Path:
    return output_dir / _folder_name(video)


def _slugify(text: str) -> str:
    lowered = text.lower()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    return re.sub(r"[\s-]+", "-", cleaned).strip("-")


def _format_date(yyyymmdd: str) -> str:
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0min"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h{minutes:02d}min"
    return f"{minutes}min"


def _build_remote_folder(
    remote_name: str,
    remote_folder: str,
    channel_name: str,
    video: ChannelVideo,
) -> str:
    year = video.upload_date[:4]
    month = video.upload_date[4:6]
    safe_title = video.title.replace("/", "-")
    return f"{remote_name}:{remote_folder}/{channel_name}/{year}/{month}/{safe_title}"


def _dry_run_result(videos: tuple[ChannelVideo, ...]) -> BatchResult:
    items = tuple(
        BatchItemResult(video=v, success=False, transcript_text=None, error=None)
        for v in videos
    )
    return BatchResult(total=len(videos), succeeded=0, failed=0, items=items)


def _success_item(video: ChannelVideo, response: TranscribeResponse) -> BatchItemResult:
    return BatchItemResult(
        video=video,
        success=True,
        transcript_text=response.text,
        error=None,
    )


def _failure_item(video: ChannelVideo, error: str) -> BatchItemResult:
    return BatchItemResult(
        video=video,
        success=False,
        transcript_text=None,
        error=error,
    )


def _build_result(items: list[BatchItemResult]) -> BatchResult:
    succeeded = sum(1 for i in items if i.success)
    failed = sum(1 for i in items if not i.success)
    return BatchResult(
        total=len(items),
        succeeded=succeeded,
        failed=failed,
        items=tuple(items),
    )
