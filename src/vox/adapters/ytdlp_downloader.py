import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from vox.adapters.download_hint import format_download_failure
from vox.models.exceptions import DownloadError
from vox.models.transcription_input import TranscriptionInput

ProcessRunner = Callable[[list[str]], subprocess.CompletedProcess]


class YtdlpDownloader:
    def __init__(
        self,
        use_cookies: bool = True,
        browser: str = "chrome",
        process_runner: ProcessRunner | None = None,
    ):
        self._use_cookies = use_cookies
        self._browser = browser
        self._run = process_runner or run_ytdlp

    def download(
        self,
        source: TranscriptionInput,
        output_dir: Path,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        template = str(output_dir / "%(title)s.%(ext)s")
        cmd = self._build_command(source.source, template)
        stdout = self._execute(cmd)
        return _find_downloaded_file(output_dir, stdout)

    def _execute(self, cmd: list[str]) -> str:
        result = self._run(cmd)
        if result.returncode != 0:
            raise DownloadError(
                format_download_failure(
                    result.stderr,
                    self._use_cookies,
                    self._browser,
                )
            )
        return result.stdout

    def _build_command(self, url: str, output_template: str) -> list[str]:
        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "-x",
            "--audio-format",
            "wav",
            "--js-runtimes",
            "node",
            "--remote-components",
            "ejs:github",
        ]
        if self._use_cookies:
            cmd += ["--cookies-from-browser", self._browser]
        cmd += ["-o", output_template, url]
        return cmd


def run_ytdlp(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )


def _find_downloaded_file(output_dir: Path, stdout: str) -> Path:
    path_from_stdout = _extract_path_from_stdout(stdout)
    if path_from_stdout and path_from_stdout.exists():
        return path_from_stdout
    return _most_recent_wav(output_dir)


def _extract_path_from_stdout(stdout: str) -> Path | None:
    for line in stdout.splitlines():
        if ".wav" not in line:
            continue
        candidate = _try_parse_destination(line)
        if candidate:
            return candidate
    return None


def _try_parse_destination(line: str) -> Path | None:
    for marker in ("Destination: ", "[ExtractAudio] Destination: "):
        if marker not in line:
            continue
        raw = line.split(marker, 1)[1].strip()
        path = Path(raw)
        if path.suffix == ".wav":
            return path
    return None


def _most_recent_wav(output_dir: Path) -> Path:
    wavs = sorted(
        output_dir.glob("*.wav"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not wavs:
        raise DownloadError("No .wav file found after download")
    return wavs[0]
