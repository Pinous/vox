from pathlib import Path


class DiskFileCleaner:
    def delete(self, path: Path) -> None:
        if path.exists():
            path.unlink()
