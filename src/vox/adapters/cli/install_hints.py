_BINARY_DEPS = ("ffmpeg", "yt-dlp")

_PLATFORM_COMMANDS = {
    "darwin": "brew install",
    "linux": "sudo apt install",
    "win32": "winget install",
}


def format_install_hint(dep_name: str, platform: str) -> str:
    if dep_name == "mlx-whisper":
        return _format_mlx_whisper(platform)
    if dep_name in _BINARY_DEPS:
        return _format_binary(dep_name, platform)
    return ""


def _format_binary(dep_name: str, platform: str) -> str:
    command = _PLATFORM_COMMANDS.get(platform)
    if not command:
        return ""
    return f"{command} {dep_name}"


def _format_mlx_whisper(platform: str) -> str:
    if platform == "darwin":
        return "uv add mlx-whisper"
    return "uv add mlx-whisper (Apple Silicon only — use --backend openai elsewhere)"
