from vox.adapters.cli.install_hints import format_install_hint


class TestFormatInstallHintFfmpeg:
    def test_format_when_ffmpeg_on_macos_then_brew(self):
        result = format_install_hint("ffmpeg", "darwin")

        assert result == "brew install ffmpeg"

    def test_format_when_ffmpeg_on_linux_then_apt(self):
        result = format_install_hint("ffmpeg", "linux")

        assert result == "sudo apt install ffmpeg"

    def test_format_when_ffmpeg_on_windows_then_winget(self):
        result = format_install_hint("ffmpeg", "win32")

        assert result == "winget install ffmpeg"


class TestFormatInstallHintYtdlp:
    def test_format_when_ytdlp_on_macos_then_brew(self):
        result = format_install_hint("yt-dlp", "darwin")

        assert result == "brew install yt-dlp"

    def test_format_when_ytdlp_on_linux_then_apt(self):
        result = format_install_hint("yt-dlp", "linux")

        assert result == "sudo apt install yt-dlp"

    def test_format_when_ytdlp_on_windows_then_winget(self):
        result = format_install_hint("yt-dlp", "win32")

        assert result == "winget install yt-dlp"


class TestFormatInstallHintMlxWhisper:
    def test_format_when_mlx_whisper_on_macos_then_uv_add(self):
        result = format_install_hint("mlx-whisper", "darwin")

        assert result == "uv add mlx-whisper"

    def test_format_when_mlx_whisper_on_linux_then_apple_silicon_warning(self):
        result = format_install_hint("mlx-whisper", "linux")

        assert "Apple Silicon" in result


class TestFormatInstallHintUnknown:
    def test_format_when_unknown_dep_then_empty(self):
        result = format_install_hint("unknown-tool", "darwin")

        assert result == ""

    def test_format_when_unknown_platform_then_empty(self):
        result = format_install_hint("ffmpeg", "freebsd")

        assert result == ""
