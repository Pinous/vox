import json
from pathlib import Path
from typing import Any


class JsonConfigStore:
    def __init__(self, config_path: Path | None = None):
        self._path = config_path or Path.home() / ".vox" / "config.json"

    def read(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text())

    def write(self, config: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(config, indent=2))

    def get(self, key: str) -> Any:
        return self.read().get(key)

    def set(self, key: str, value: Any) -> None:
        config = self.read()
        config[key] = value
        self.write(config)
