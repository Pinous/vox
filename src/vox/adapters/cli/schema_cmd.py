import json
import sys
from importlib import resources

import click

from vox.models.exceptions import VoxError


@click.command()
@click.argument("command", default="transcribe")
def schema(command):
    try:
        result = _load_schema(command)
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(json.dumps(result, indent=2))


def _load_schema(command: str) -> dict:
    filename = f"{command}.json"
    try:
        ref = resources.files("vox.schemas").joinpath(filename)
        content = ref.read_text(encoding="utf-8")
        return json.loads(content)
    except (FileNotFoundError, ModuleNotFoundError, TypeError) as err:
        raise VoxError(f"Schema not found: {command}") from err
