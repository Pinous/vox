import subprocess
import sys
from pathlib import Path

from vox.models.exceptions import DownloadError
from vox.models.transcription_input import TranscriptionInput


class YtdlpDownloader:
    def download(
        self,
        source: TranscriptionInput,
        output_dir: Path,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        template = str(output_dir / "%(title)s.%(ext)s")
        cmd = _build_command(source.source, template)
        stdout = _run_ytdlp(cmd)
        return _find_downloaded_file(output_dir, stdout)


def _build_command(url: str, output_template: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "-x",
        "--audio-format",
        "wav",
        "-o",
        output_template,
        url,
    ]


def _run_ytdlp(cmd: list[str]) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise DownloadError(f"yt-dlp failed: {result.stderr}")
    return result.stdout


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
