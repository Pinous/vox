from dataclasses import dataclass

from vox.models.whisper_model import WhisperModel
from vox.ports.config_store import ConfigStore
from vox.ports.dependency_checker import DependencyChecker, HealthStatus
from vox.ports.model_manager import ModelManager
from vox.ports.progress_reporter import ProgressReporter


@dataclass(frozen=True)
class InitRequest:
    model: str = "small"
    language: str = "auto"


@dataclass(frozen=True)
class InitResponse:
    success: bool
    model: str
    model_repo: str
    language: str
    missing_deps: list[str]


class InitDepsUseCase:
    def __init__(
        self,
        model_manager: ModelManager,
        config: ConfigStore,
        progress: ProgressReporter,
        checker: DependencyChecker,
    ):
        self._model_manager = model_manager
        self._config = config
        self._progress = progress
        self._checker = checker

    def execute(self, request: InitRequest) -> InitResponse:
        missing = _find_missing(self._checker.check_all())
        whisper_model = WhisperModel.from_string(request.model)
        self._progress.start(f"Downloading {request.model}")
        repo = self._model_manager.ensure_model(whisper_model)
        self._config.set("model", request.model)
        self._config.set("language", request.language)
        self._progress.finish()
        return InitResponse(
            success=True,
            model=request.model,
            model_repo=repo,
            language=request.language,
            missing_deps=missing,
        )


def _find_missing(deps: list[HealthStatus]) -> list[str]:
    return [dep.name for dep in deps if not dep.installed]
