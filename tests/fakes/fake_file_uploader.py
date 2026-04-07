from pathlib import Path


class FakeFileUploader:
    def __init__(self):
        self.uploads: list[tuple[Path, str]] = []

    def upload(self, local_path: Path, remote_folder: str) -> None:
        self.uploads.append((local_path, remote_folder))
