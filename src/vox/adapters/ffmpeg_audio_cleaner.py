import subprocess
from pathlib import Path

from vox.models.audio_config import AudioConfig
from vox.models.exceptions import AudioCleaningError


class FfmpegAudioCleaner:
    def clean(
        self,
        input_path: Path,
        config: AudioConfig,
        output_path: Path,
    ) -> Path:
        cmd = _build_command(input_path, config, output_path)
        _run_ffmpeg(cmd)
        return output_path


def _build_command(
    input_path: Path,
    config: AudioConfig,
    output_path: Path,
) -> list[str]:
    filters = _build_filter_chain(config)
    return [
        "ffmpeg",
        "-i",
        str(input_path),
        "-af",
        ",".join(filters),
        "-ar",
        str(config.sample_rate),
        "-ac",
        str(config.channels),
        "-f",
        "wav",
        "-acodec",
        "pcm_s16le",
        str(output_path),
        "-y",
    ]


def _build_filter_chain(config: AudioConfig) -> list[str]:
    filters: list[str] = []
    if config.remove_silence:
        filters.append(
            "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-40dB"
        )
    if config.denoise:
        filters.append("afftdn=nf=-25")
    if config.normalize:
        filters.append("dynaudnorm")
    return filters


def _run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace")
        raise AudioCleaningError(f"ffmpeg failed: {stderr}")
