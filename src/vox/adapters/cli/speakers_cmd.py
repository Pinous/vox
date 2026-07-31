import json as json_mod
import sys

import click

from vox.adapters.json_voice_print_store import JsonVoicePrintStore
from vox.adapters.sherpa_voice_print_extractor import SherpaVoicePrintExtractor
from vox.models.exceptions import VoxError
from vox.use_cases.enroll_speaker import EnrollSpeakerRequest, EnrollSpeakerUseCase


@click.group()
def speakers():
    """Manage known voices used by --identify."""


@speakers.command()
@click.argument("name")
@click.option("--from", "source", required=True, help="Audio/video file to sample")
@click.option(
    "--at",
    required=True,
    help="Time span of clean speech, in seconds: START-END (e.g. 120-140)",
)
def add(name, source, at):
    """Register NAME's voice from a span of audio."""
    try:
        start, end = _parse_span(at)
        response = EnrollSpeakerUseCase(
            extractor=SherpaVoicePrintExtractor(),
            store=JsonVoicePrintStore(),
        ).execute(
            EnrollSpeakerRequest(
                name=name,
                audio_path=source,
                start=start,
                end=end,
            )
        )
    except VoxError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    click.echo(
        json_mod.dumps(
            {"name": response.name, "seconds_used": response.seconds_used},
            indent=2,
        )
    )


@speakers.command(name="list")
def list_speakers():
    """List registered voices."""
    prints = JsonVoicePrintStore().load_all()
    click.echo(json_mod.dumps({"speakers": [p.name for p in prints]}, indent=2))


def _parse_span(raw: str) -> tuple[float, float]:
    parts = raw.split("-")
    if len(parts) != 2:
        raise VoxError(f"invalid span '{raw}', expected START-END (e.g. 120-140)")
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        raise VoxError(f"invalid span '{raw}', expected numbers in seconds") from None
