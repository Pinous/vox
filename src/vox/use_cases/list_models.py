from vox.models.openai_model import OpenAIModel
from vox.models.transcription_backend import TranscriptionBackend
from vox.models.whisper_model import WhisperModel


class ListModelsUseCase:
    def execute(self, backend: str | None) -> dict[str, tuple[str, ...]]:
        if backend is None:
            return {name: _models_for(name) for name in _backend_names()}
        resolved = TranscriptionBackend.from_string(backend)
        return {resolved.value: _models_for(resolved.value)}


def _backend_names() -> tuple[str, ...]:
    return tuple(backend.value for backend in TranscriptionBackend)


def _models_for(backend_name: str) -> tuple[str, ...]:
    if backend_name == TranscriptionBackend.OPENAI.value:
        return tuple(model.api_name for model in OpenAIModel)
    return tuple(model.cli_name for model in WhisperModel)
