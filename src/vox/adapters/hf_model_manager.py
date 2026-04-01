from huggingface_hub import snapshot_download

from vox.models.whisper_model import WhisperModel


class HfModelManager:
    def ensure_model(self, model: WhisperModel) -> str:
        return snapshot_download(model.hf_repo)

    def is_cached(self, model: WhisperModel) -> bool:
        try:
            from huggingface_hub import try_to_load_from_cache

            result = try_to_load_from_cache(
                model.hf_repo,
                "config.json",
            )
            return result is not None
        except Exception:
            return False
