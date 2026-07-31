from vox.models.exceptions import DiarizationError

SEGMENTATION_REPO = "csukuangfj/sherpa-onnx-pyannote-segmentation-3-0"
SEGMENTATION_FILE = "model.onnx"
EMBEDDING_REPO = "csukuangfj/speaker-embedding-models"
EMBEDDING_FILE = "wespeaker_en_voxceleb_resnet34_LM.onnx"


def ensure_model(repo: str, filename: str) -> str:
    from huggingface_hub import hf_hub_download

    try:
        return hf_hub_download(repo_id=repo, filename=filename)
    except Exception as e:
        raise DiarizationError(f"cannot download {filename} from {repo}: {e}") from e


def import_sherpa():
    try:
        import sherpa_onnx
    except ImportError as e:
        raise DiarizationError(
            "sherpa-onnx not installed. Run: uv add sherpa-onnx sherpa-onnx-core"
        ) from e
    return sherpa_onnx
