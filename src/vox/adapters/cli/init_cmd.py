import sys

import click

from vox.adapters.cli.output_formatter import format_output
from vox.adapters.click_progress import ClickProgressReporter
from vox.adapters.hf_model_manager import HfModelManager
from vox.adapters.json_config_store import JsonConfigStore
from vox.adapters.system_dep_checker import SystemDependencyChecker
from vox.models.exceptions import VoxError
from vox.use_cases.init_deps import InitDepsUseCase, InitRequest


@click.command()
@click.option("-m", "--model", default="small", help="tiny|base|small|medium|large-v3")
@click.option("-l", "--language", default="auto", help="Language code or auto")
@click.option("--format", "fmt", default=None, help="json|table")
def init(model, language, fmt):
    use_case = InitDepsUseCase(
        model_manager=HfModelManager(),
        config=JsonConfigStore(),
        progress=ClickProgressReporter(),
        checker=SystemDependencyChecker(),
    )
    try:
        response = use_case.execute(
            InitRequest(model=model, language=language),
        )
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(format_output(response, None, fmt))
