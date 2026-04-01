import json
from pathlib import Path

from vox.models.exceptions import VoxError


class GetSchemaUseCase:
    def __init__(self, schemas_dir: Path):
        self._schemas_dir = schemas_dir

    def execute(self, command: str) -> dict:
        schema_path = self._schemas_dir / f"{command}.json"
        if not schema_path.exists():
            raise VoxError(f"Schema not found: {command}")
        return json.loads(schema_path.read_text())
