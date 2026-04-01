from typing import Any


class FakeConfigStore:
    def __init__(self, initial: dict[str, Any] | None = None):
        self._data: dict[str, Any] = initial or {}

    def read(self) -> dict[str, Any]:
        return dict(self._data)

    def write(self, config: dict[str, Any]) -> None:
        self._data = dict(config)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
