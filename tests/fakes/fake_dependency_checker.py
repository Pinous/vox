from vox.ports.dependency_checker import HealthStatus


class FakeDependencyChecker:
    def __init__(
        self,
        statuses: list[HealthStatus] | None = None,
    ):
        self._statuses = statuses or _all_healthy()

    def check_all(self) -> list[HealthStatus]:
        return self._statuses


def _all_healthy() -> list[HealthStatus]:
    return [
        HealthStatus("yt-dlp", True, "2024.1.1", "/usr/local/bin/yt-dlp"),
        HealthStatus("ffmpeg", True, "6.0", "/usr/local/bin/ffmpeg"),
        HealthStatus("mlx-whisper", True, "0.4.0"),
    ]
