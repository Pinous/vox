from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from vox.models.audio_config import AudioConfig
from vox.models.exceptions import ValidationError
from vox.models.language import Language
from vox.models.transcription_input import TranscriptionInput
from vox.models.whisper_model import WhisperModel
from vox.ports.audio_cleaner import AudioCleaner
from vox.ports.downloader import Downloader
from vox.ports.file_writer import FileWriter
from vox.ports.progress_reporter import ProgressReporter
from vox.ports.transcriber import Transcriber


@dataclass(frozen=True)
class TranscribeRequest:
    source: str
    language: str = "auto"
    model: str = "small"
    output_dir: str = "."
    word_timestamps: bool = False
    no_clean: bool = False
    no_download: bool = False
    dry_run: bool = False
    output_stem: str = ""


@dataclass(frozen=True)
class TranscribeResponse:
    text: str
    language: str
    srt_path: str
    txt_path: str
    json_path: str
    wav_path: str | None


class TranscribeUseCase:
    def __init__(
        self,
        downloader: Downloader,
        audio_cleaner: AudioCleaner,
        transcriber: Transcriber,
        file_writer: FileWriter,
        progress: ProgressReporter,
    ):
        self._downloader = downloader
        self._audio_cleaner = audio_cleaner
        self._transcriber = transcriber
        self._file_writer = file_writer
        self._progress = progress

    def execute(self, request: TranscribeRequest) -> TranscribeResponse:
        self._progress.start("Validating input")
        parsed_input = TranscriptionInput.from_string(request.source)
        _reject_no_download_with_url(request.no_download, parsed_input)
        language = Language.from_string(request.language)
        model = WhisperModel.from_string(request.model)
        output_dir = Path(request.output_dir)

        if request.dry_run:
            return _dry_run_response(request, parsed_input, output_dir)

        audio_path = self._resolve_audio(parsed_input, output_dir)
        wav_path = self._maybe_clean(audio_path, request.no_clean, output_dir)
        result = self._transcribe(wav_path or audio_path, model, language, request)
        paths = self._write_outputs(
            result, output_dir, parsed_input, request.output_stem
        )
        self._progress.finish()
        return _build_response(result, paths, wav_path)

    def _resolve_audio(
        self, parsed_input: TranscriptionInput, output_dir: Path
    ) -> Path:
        if not parsed_input.is_url:
            return Path(parsed_input.source)
        self._progress.update("Downloading")
        return self._downloader.download(parsed_input, output_dir)

    def _maybe_clean(
        self, audio_path: Path, no_clean: bool, output_dir: Path
    ) -> Path | None:
        if no_clean:
            return None
        self._progress.update("Cleaning audio")
        clean_path = output_dir / f"{audio_path.stem}_clean.wav"
        return self._audio_cleaner.clean(audio_path, AudioConfig.default(), clean_path)

    def _transcribe(self, audio_path, model, language, request):
        self._progress.update("Transcribing")
        lang_code = None if language.code == "auto" else language.code
        return self._transcriber.transcribe(
            audio_path, model, lang_code, request.word_timestamps
        )

    def _write_outputs(self, result, output_dir, parsed_input, output_stem):
        self._progress.update("Writing outputs")
        stem = output_stem or _derive_output_stem(parsed_input)
        srt_path = output_dir / f"{stem}.srt"
        txt_path = output_dir / f"{stem}.txt"
        json_path = output_dir / f"{stem}.json"
        self._file_writer.write_srt(result, srt_path)
        self._file_writer.write_txt(result, txt_path)
        self._file_writer.write_json(result, json_path)
        return srt_path, txt_path, json_path


def _reject_no_download_with_url(
    no_download: bool, parsed_input: TranscriptionInput
) -> None:
    if no_download and parsed_input.is_url:
        raise ValidationError("Cannot use --no-download with URL input")


def _derive_output_stem(parsed_input: TranscriptionInput) -> str:
    if parsed_input.is_url:
        return f"vox_{int(time.time())}"
    return Path(parsed_input.source).stem


def _dry_run_response(
    request: TranscribeRequest,
    parsed_input: TranscriptionInput,
    output_dir: Path,
) -> TranscribeResponse:
    plan = _build_execution_plan(request, parsed_input)
    return TranscribeResponse(
        text=plan,
        language=request.language,
        srt_path=str(output_dir / "output.srt"),
        txt_path=str(output_dir / "output.txt"),
        json_path=str(output_dir / "output.json"),
        wav_path=None,
    )


def _build_execution_plan(
    request: TranscribeRequest,
    parsed_input: TranscriptionInput,
) -> str:
    input_type = "url" if parsed_input.is_url else "file"
    steps = [f"Validate input: {parsed_input.source} ({input_type})"]
    if parsed_input.is_url and not request.no_download:
        steps.append("Download via yt-dlp")
    if not request.no_clean:
        steps.append("Clean audio via ffmpeg")
    lang = request.language
    steps.append(f"Transcribe with model '{request.model}', language '{lang}'")
    steps.append("Write outputs: .srt, .txt, .json")
    numbered = [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    return "Execution plan:\n" + "\n".join(numbered)


def _build_response(result, paths, wav_path) -> TranscribeResponse:
    srt_path, txt_path, json_path = paths
    return TranscribeResponse(
        text=result.text,
        language=result.language,
        srt_path=str(srt_path),
        txt_path=str(txt_path),
        json_path=str(json_path),
        wav_path=str(wav_path) if wav_path else None,
    )
