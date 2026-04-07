from pathlib import Path

from vox.models.video_metadata import VideoMetadata


class FakeMetadataWriter:
    def __init__(self):
        self.metas_written: list[tuple[VideoMetadata, Path]] = []
        self.index_written: list[tuple[tuple[VideoMetadata, ...], Path]] = []
        self.claude_md_written: list[Path] = []

    def write_meta(self, metadata: VideoMetadata, folder: Path) -> None:
        self.metas_written.append((metadata, folder))

    def write_index(
        self, all_metadata: tuple[VideoMetadata, ...], output_dir: Path
    ) -> None:
        self.index_written.append((all_metadata, output_dir))

    def write_claude_md(self, output_dir: Path) -> None:
        self.claude_md_written.append(output_dir)
