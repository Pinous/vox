import json
import sys

import click

from vox.adapters.cli.output_formatter import resolve_format
from vox.models.exceptions import VoxError
from vox.use_cases.list_models import ListModelsUseCase


@click.command()
@click.option("-b", "--backend", default=None, help="local | openai")
@click.option("--format", "fmt", default=None, help="json|table")
def models(backend, fmt):
    try:
        listed = ListModelsUseCase().execute(backend)
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(_render(listed, resolve_format(fmt)))


def _render(listed: dict[str, tuple[str, ...]], output_format: str) -> str:
    if output_format == "json":
        return json.dumps({k: list(v) for k, v in listed.items()}, indent=2)
    return _format_table(listed)


def _format_table(listed: dict[str, tuple[str, ...]]) -> str:
    max_backend = max(len(name) for name in listed)
    rows = [
        f"  {name.ljust(max_backend)}  {model}"
        for name, models_for_backend in listed.items()
        for model in models_for_backend
    ]
    return "\n".join(rows)
