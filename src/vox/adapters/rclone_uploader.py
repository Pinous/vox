import subprocess
from pathlib import Path

from vox.models.exceptions import UploadError


class RcloneUploader:
    def upload(self, local_path: Path, remote_folder: str) -> None:
        cmd = _build_command(local_path, remote_folder)
        _run_rclone(cmd)


def _build_command(local_path: Path, remote_folder: str) -> list[str]:
    return [
        "rclone",
        "copy",
        str(local_path),
        remote_folder,
    ]


def _run_rclone(cmd: list[str]) -> None:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise UploadError(f"rclone failed: {result.stderr}")
