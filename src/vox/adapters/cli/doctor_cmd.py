import json
import sys

import click

from vox.adapters.hf_model_manager import HfModelManager
from vox.adapters.json_config_store import JsonConfigStore
from vox.adapters.system_dep_checker import SystemDependencyChecker
from vox.use_cases.check_health import CheckHealthUseCase


@click.command()
@click.option("--format", "fmt", default=None, help="json|table")
def doctor(fmt):
    use_case = CheckHealthUseCase(
        checker=SystemDependencyChecker(),
        config=JsonConfigStore(),
        model_manager=HfModelManager(),
    )
    report = use_case.execute()
    if _wants_json(fmt):
        click.echo(json.dumps(_to_dict(report), indent=2))
        return
    _print_table(report)
    sys.exit(0 if report.healthy else 1)


def _wants_json(fmt: str | None) -> bool:
    if fmt == "json":
        return True
    return fmt is None and not sys.stdout.isatty()


def _to_dict(report) -> dict:
    return {
        "healthy": report.healthy,
        "dependencies": [
            {
                "name": d.name,
                "installed": d.installed,
                "version": d.version,
                "path": d.path,
            }
            for d in report.dependencies
        ],
        "config_exists": report.config_exists,
        "model": report.model_name,
        "model_cached": report.model_cached,
    }


def _print_table(report) -> None:
    for dep in report.dependencies:
        icon = "+" if dep.installed else "x"
        version = dep.version or "not found"
        click.echo(f"  [{icon}] {dep.name}: {version}")
    click.echo(
        f"  Config: {'found' if report.config_exists else 'missing'}",
    )
    if report.model_name:
        cached = "cached" if report.model_cached else "not cached"
        click.echo(f"  Model: {report.model_name} ({cached})")
    status = "healthy" if report.healthy else "unhealthy"
    click.echo(f"\n  Status: {status}")
