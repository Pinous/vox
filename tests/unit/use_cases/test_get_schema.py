import json

import pytest

from vox.models.exceptions import VoxError
from vox.use_cases.get_schema import GetSchemaUseCase


class TestGetSchema:
    def test_execute_when_schema_exists_then_returns_dict(self, tmp_path):
        schema = {"type": "object", "properties": {"url": {"type": "string"}}}
        schema_file = tmp_path / "download.json"
        schema_file.write_text(json.dumps(schema))
        use_case = GetSchemaUseCase(tmp_path)

        result = use_case.execute("download")

        assert result == schema

    def test_execute_when_schema_missing_then_raises(self, tmp_path):
        use_case = GetSchemaUseCase(tmp_path)

        with pytest.raises(VoxError):
            use_case.execute("nonexistent")
