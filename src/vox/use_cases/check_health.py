import os
from dataclasses import dataclass

from vox.models.whisper_model import WhisperModel
from vox.ports.config_store import ConfigStore
from vox.ports.dependency_checker import DependencyChecker, HealthStatus
from vox.ports.model_manager import ModelManager


@dataclass(frozen=True)
class HealthReport:
    healthy: bool
    dependencies: list[HealthStatus]
    config_exists: bool
    model_name: str | None
    model_cached: bool
    openai_api_key_set: bool


class CheckHealthUseCase:
    def __init__(
        self,
        checker: DependencyChecker,
        config: ConfigStore,
        model_manager: ModelManager,
    ):
        self._checker = checker
        self._config = config
        self._model_manager = model_manager

    def execute(self) -> HealthReport:
        dependencies = self._checker.check_all()
        model_name = self._config.get("model")
        return HealthReport(
            healthy=_all_installed(dependencies),
            dependencies=dependencies,
            config_exists=_config_readable(self._config),
            model_name=model_name,
            model_cached=_check_cached(
                self._model_manager,
                model_name,
            ),
            openai_api_key_set=bool(os.environ.get("OPENAI_API_KEY")),
        )


def _all_installed(deps: list[HealthStatus]) -> bool:
    return all(dep.installed for dep in deps)


def _config_readable(config: ConfigStore) -> bool:
    try:
        config.read()
        return True
    except Exception:
        return False


def _check_cached(
    manager: ModelManager,
    model_name: str | None,
) -> bool:
    if not model_name:
        return False
    return manager.is_cached(WhisperModel.from_string(model_name))
