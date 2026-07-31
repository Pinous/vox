import subprocess
from pathlib import Path

from vox.models.exceptions import DiarizationError

SAMPLE_RATE = 16000


def decode_to_mono_16k(audio_path: Path):
    import numpy as np

    result = subprocess.run(
        _ffmpeg_decode_command(audio_path),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace")
        raise DiarizationError(f"ffmpeg failed to decode audio: {stderr}")
    return np.frombuffer(result.stdout, dtype=np.float32)


def slice_samples(samples, start: float, end: float):
    return samples[int(start * SAMPLE_RATE) : int(end * SAMPLE_RATE)]


def _ffmpeg_decode_command(audio_path: Path) -> list[str]:
    return [
        "ffmpeg",
        "-v",
        "quiet",
        "-i",
        str(audio_path),
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        "1",
        "-f",
        "f32le",
        "-",
    ]
