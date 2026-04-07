import sys

import click

from vox.adapters.cli.channel_cmd import channel
from vox.adapters.cli.doctor_cmd import doctor
from vox.adapters.cli.init_cmd import init
from vox.adapters.cli.schema_cmd import schema
from vox.adapters.cli.transcribe_cmd import transcribe


class DefaultTranscribeGroup(click.Group):
    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = ["transcribe", *args]
        return super().parse_args(ctx, args)


@click.group(cls=DefaultTranscribeGroup)
def main() -> None:
    pass


main.add_command(transcribe)
main.add_command(channel)
main.add_command(init)
main.add_command(doctor)
main.add_command(schema)


def _is_agent_mode() -> bool:
    return not sys.stdout.isatty()
