import click


class ClickProgressReporter:
    def start(self, label: str) -> None:
        click.echo(f"-> {label}", err=True)

    def update(self, label: str) -> None:
        click.echo(f"  {label}", err=True)

    def finish(self) -> None:
        click.echo("Done", err=True)
