from pathlib import Path
from typing import Protocol


class FileCleaner(Protocol):
    def delete(self, path: Path) -> None: ...
