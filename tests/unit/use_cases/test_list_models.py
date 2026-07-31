import pytest

from vox.models.exceptions import ValidationError
from vox.use_cases.list_models import ListModelsUseCase


class TestListModelsUseCase:
    def test_execute_when_no_backend_then_lists_every_backend(self):
        result = ListModelsUseCase().execute(None)

        assert set(result) == {"local", "openai"}

    def test_execute_when_local_backend_then_lists_only_local(self):
        result = ListModelsUseCase().execute("local")

        assert set(result) == {"local"}

    def test_execute_when_openai_backend_then_lists_only_openai(self):
        result = ListModelsUseCase().execute("openai")

        assert set(result) == {"openai"}

    def test_execute_when_local_backend_then_returns_cli_model_names(self):
        result = ListModelsUseCase().execute("local")

        assert result["local"] == (
            "tiny",
            "base",
            "small",
            "medium",
            "large-v3",
            "large-v3-turbo",
        )

    def test_execute_when_openai_backend_then_returns_api_model_names(self):
        result = ListModelsUseCase().execute("openai")

        assert result["openai"] == (
            "gpt-4o-transcribe",
            "gpt-4o-mini-transcribe",
            "whisper-1",
        )

    def test_execute_when_unknown_backend_then_raises(self):
        with pytest.raises(ValidationError, match="Unknown backend"):
            ListModelsUseCase().execute("vercel")
