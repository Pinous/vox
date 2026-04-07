from tests.fakes.fake_config_store import FakeConfigStore
from tests.fakes.fake_dependency_checker import FakeDependencyChecker
from tests.fakes.fake_model_manager import FakeModelManager
from vox.ports.dependency_checker import HealthStatus
from vox.use_cases.check_health import CheckHealthUseCase


class TestCheckHealth:
    def test_execute_when_all_healthy_then_healthy_true(self):
        use_case = _build_use_case(
            config=FakeConfigStore({"model": "small"}),
        )

        report = use_case.execute()

        assert report.healthy is True
        assert report.config_exists is True
        assert len(report.dependencies) == 3
        assert report.model_cached is True

    def test_execute_when_missing_dep_then_healthy_false(self):
        statuses = [
            HealthStatus("yt-dlp", False),
            HealthStatus("ffmpeg", True, "6.0"),
        ]
        use_case = _build_use_case(
            checker=FakeDependencyChecker(statuses),
        )

        report = use_case.execute()

        assert report.healthy is False

    def test_execute_when_config_has_model_then_model_name_set(self):
        use_case = _build_use_case(
            config=FakeConfigStore({"model": "large-v3"}),
        )

        report = use_case.execute()

        assert report.model_name == "large-v3"

    def test_execute_when_model_cached_then_model_cached_true(self):
        use_case = _build_use_case(
            config=FakeConfigStore({"model": "small"}),
            model_manager=FakeModelManager(cached=True),
        )

        report = use_case.execute()

        assert report.model_cached is True

    def test_execute_when_no_model_then_model_cached_false(self):
        use_case = _build_use_case(
            config=FakeConfigStore(),
            model_manager=FakeModelManager(cached=True),
        )

        report = use_case.execute()

        assert report.model_name is None
        assert report.model_cached is False

    def test_execute_when_openai_key_set_then_openai_status_set(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        use_case = _build_use_case()

        report = use_case.execute()

        assert report.openai_api_key_set is True

    def test_execute_when_openai_key_unset_then_openai_status_false(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        use_case = _build_use_case()

        report = use_case.execute()

        assert report.openai_api_key_set is False


def _build_use_case(
    checker: FakeDependencyChecker | None = None,
    config: FakeConfigStore | None = None,
    model_manager: FakeModelManager | None = None,
) -> CheckHealthUseCase:
    return CheckHealthUseCase(
        checker=checker or FakeDependencyChecker(),
        config=config or FakeConfigStore(),
        model_manager=model_manager or FakeModelManager(),
    )
