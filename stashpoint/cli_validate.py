"""CLI commands for snapshot validation."""

import click
from stashpoint.validate import validate_snapshot, SnapshotNotFoundError


@click.group("validate")
def validate_cmd():
    """Validate snapshot keys against required/forbidden rules."""


@validate_cmd.command("run")
@click.argument("name")
@click.option(
    "--require",
    "required",
    multiple=True,
    metavar="KEY",
    help="Key that must be present in the snapshot.",
)
@click.option(
    "--forbid",
    "forbidden",
    multiple=True,
    metavar="KEY",
    help="Key that must NOT be present in the snapshot.",
)
def validate_run_cmd(name: str, required: tuple, forbidden: tuple):
    """Validate snapshot NAME against key rules."""
    try:
        result = validate_snapshot(
            name,
            required=list(required),
            forbidden=list(forbidden),
        )
    except SnapshotNotFoundError as e:
        raise click.ClickException(str(e))

    click.echo(result.summary())
    if not result.is_valid:
        raise SystemExit(1)
