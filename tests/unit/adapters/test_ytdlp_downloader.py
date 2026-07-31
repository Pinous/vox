import subprocess
from pathlib import Path

import pytest

from vox.adapters.ytdlp_downloader import YtdlpDownloader
from vox.models.exceptions import DownloadError
from vox.models.transcription_input import TranscriptionInput


def _recording_runner(output_dir: Path, commands: list, returncode=0, stderr=""):
    def runner(cmd: list[str]) -> subprocess.CompletedProcess:
        commands.append(cmd)
        if returncode == 0:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "video.wav").write_bytes(b"")
        return subprocess.CompletedProcess(cmd, returncode, "", stderr)

    return runner


class TestYtdlpDownloaderCookies:
    def test_download_when_default_browser_then_command_uses_chrome(self, tmp_path):
        commands: list = []
        downloader = YtdlpDownloader(
            process_runner=_recording_runner(tmp_path, commands)
        )

        downloader.download(TranscriptionInput.from_string("https://x.com/v"), tmp_path)

        assert "--cookies-from-browser" in commands[0]
        assert "chrome" in commands[0]

    def test_download_when_browser_is_firefox_then_command_uses_firefox(self, tmp_path):
        commands: list = []
        downloader = YtdlpDownloader(
            browser="firefox",
            process_runner=_recording_runner(tmp_path, commands),
        )

        downloader.download(TranscriptionInput.from_string("https://x.com/v"), tmp_path)

        assert "firefox" in commands[0]
        assert "chrome" not in commands[0]

    def test_download_when_cookies_disabled_then_command_omits_cookies_flag(
        self, tmp_path
    ):
        commands: list = []
        downloader = YtdlpDownloader(
            use_cookies=False,
            process_runner=_recording_runner(tmp_path, commands),
        )

        downloader.download(TranscriptionInput.from_string("https://x.com/v"), tmp_path)

        assert "--cookies-from-browser" not in commands[0]


class TestYtdlpDownloaderFailureHint:
    def test_download_when_auth_failure_without_cookies_then_error_hints_cookies(
        self, tmp_path
    ):
        runner = _recording_runner(
            tmp_path,
            [],
            returncode=1,
            stderr="ERROR: Sign in to confirm you are not a bot",
        )
        downloader = YtdlpDownloader(use_cookies=False, process_runner=runner)

        with pytest.raises(DownloadError) as exc:
            downloader.download(
                TranscriptionInput.from_string("https://x.com/v"), tmp_path
            )

        assert "--no-cookies" in str(exc.value)

    def test_download_when_plain_failure_then_error_has_no_hint(self, tmp_path):
        runner = _recording_runner(
            tmp_path, [], returncode=1, stderr="ffmpeg not found"
        )
        downloader = YtdlpDownloader(process_runner=runner)

        with pytest.raises(DownloadError) as exc:
            downloader.download(
                TranscriptionInput.from_string("https://x.com/v"), tmp_path
            )

        assert "--browser" not in str(exc.value)
