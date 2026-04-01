import shutil
import subprocess

from vox.ports.dependency_checker import HealthStatus


class SystemDependencyChecker:
    def check_all(self) -> list[HealthStatus]:
        return [
            _check_python_module("yt_dlp", "yt-dlp"),
            _check_binary("ffmpeg"),
            _check_python_module("mlx_whisper", "mlx-whisper"),
        ]


def _check_binary(name: str) -> HealthStatus:
    path = shutil.which(name)
    if not path:
        return HealthStatus(name, False)
    version = _get_version(name)
    return HealthStatus(name, True, version, path)


def _get_version(name: str) -> str | None:
    try:
        result = subprocess.run(
            [name, "--version"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().split("\n")[0]
    except Exception:
        return None


def _check_python_module(
    module_name: str,
    display_name: str,
) -> HealthStatus:
    try:
        mod = __import__(module_name)
        version = _extract_version(mod)
        return HealthStatus(display_name, True, version)
    except ImportError:
        return HealthStatus(display_name, False)


def _extract_version(mod: object) -> str:
    for attr in ("__version__", "version"):
        val = getattr(mod, attr, None)
        if isinstance(val, str):
            return val
    version_mod = getattr(mod, "version", None)
    if version_mod and hasattr(version_mod, "__version__"):
        return version_mod.__version__
    return "installed"
