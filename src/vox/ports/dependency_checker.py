from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HealthStatus:
    name: str
    installed: bool
    version: str | None = None
    path: str | None = None


class DependencyChecker(Protocol):
    def check_all(self) -> list[HealthStatus]: ...
