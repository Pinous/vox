from pathlib import Path
from typing import Protocol

from vox.models.video_metadata import VideoMetadata


class MetadataWriter(Protocol):
    def write_meta(self, metadata: VideoMetadata, folder: Path) -> None: ...

    def write_index(
        self, all_metadata: tuple[VideoMetadata, ...], output_dir: Path
    ) -> None: ...

    def write_claude_md(self, output_dir: Path) -> None: ...
