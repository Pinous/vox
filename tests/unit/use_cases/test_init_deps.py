import pytest

from tests.fakes.fake_config_store import FakeConfigStore
from tests.fakes.fake_dependency_checker import FakeDependencyChecker
from tests.fakes.fake_model_manager import FakeModelManager
from tests.fakes.fake_progress import FakeProgressReporter
from vox.models.exceptions import ValidationError
from vox.ports.dependency_checker import HealthStatus
from vox.use_cases.init_deps import InitDepsUseCase, InitRequest


class TestInitDeps:
    def test_execute_when_valid_model_then_downloads(self):
        use_case = _build_use_case()

        response = use_case.execute(InitRequest(model="small"))

        assert response.success is True
        assert response.model == "small"
        assert response.model_repo == "mlx-community/whisper-small-mlx"
        assert response.language == "auto"
        assert response.missing_deps == []

    def test_execute_when_valid_then_saves_config(self):
        config = FakeConfigStore()
        use_case = _build_use_case(config=config)

        use_case.execute(InitRequest(model="small"))

        assert config.get("model") == "small"

    def test_execute_when_invalid_model_then_raises(self):
        use_case = _build_use_case()

        with pytest.raises(ValidationError):
            use_case.execute(InitRequest(model="nonexistent"))

    def test_execute_when_missing_dep_then_reports_in_response(self):
        statuses = [
            HealthStatus("yt-dlp", False),
            HealthStatus("ffmpeg", True, "6.0"),
            HealthStatus("mlx-whisper", True, "0.4.0"),
        ]
        checker = FakeDependencyChecker(statuses)
        use_case = _build_use_case(checker=checker)

        response = use_case.execute(InitRequest(model="small"))

        assert response.missing_deps == ["yt-dlp"]

    def test_execute_when_language_set_then_saves_to_config(self):
        config = FakeConfigStore()
        use_case = _build_use_case(config=config)

        use_case.execute(InitRequest(model="small", language="fr"))

        assert config.get("language") == "fr"


def _build_use_case(
    manager: FakeModelManager | None = None,
    config: FakeConfigStore | None = None,
    progress: FakeProgressReporter | None = None,
    checker: FakeDependencyChecker | None = None,
) -> InitDepsUseCase:
    return InitDepsUseCase(
        model_manager=manager or FakeModelManager(),
        config=config or FakeConfigStore(),
        progress=progress or FakeProgressReporter(),
        checker=checker or FakeDependencyChecker(),
    )
