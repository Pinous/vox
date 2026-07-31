import json

from click.testing import CliRunner

from vox.adapters.cli.models_cmd import models


class TestModelsCommand:
    def test_models_when_json_format_then_lists_every_backend(self):
        result = CliRunner().invoke(models, ["--format", "json"])

        payload = json.loads(result.output)
        assert set(payload) == {"local", "openai"}
        assert "large-v3-turbo" in payload["local"]
        assert "gpt-4o-transcribe" in payload["openai"]

    def test_models_when_backend_filter_then_lists_only_that_backend(self):
        result = CliRunner().invoke(models, ["-b", "openai", "--format", "json"])

        assert set(json.loads(result.output)) == {"openai"}

    def test_models_when_table_format_then_pairs_backend_and_model(self):
        result = CliRunner().invoke(models, ["-b", "local", "--format", "table"])

        assert "local" in result.output
        assert "small" in result.output
        assert result.output.count("local") == len(result.output.strip().splitlines())

    def test_models_when_unknown_backend_then_exits_with_error(self):
        result = CliRunner().invoke(models, ["-b", "vercel"])

        assert result.exit_code == 1
        assert "Unknown backend" in result.output
