from pathlib import Path


class FakeFileCleaner:
    def __init__(self):
        self.deleted: list[Path] = []

    def delete(self, path: Path) -> None:
        self.deleted.append(path)
