from vox.models.whisper_model import WhisperModel


class FakeModelManager:
    def __init__(self, cached: bool = True):
        self._cached = cached
        self.ensure_called_with: WhisperModel | None = None

    def ensure_model(self, model: WhisperModel) -> str:
        self.ensure_called_with = model
        return model.hf_repo

    def is_cached(self, model: WhisperModel) -> bool:
        return self._cached
