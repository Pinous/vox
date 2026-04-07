from pathlib import Path
from typing import Protocol


class FileUploader(Protocol):
    def upload(self, local_path: Path, remote_folder: str) -> None: ...
