"""CLI commands for copying snapshots."""

import click

from stashpoint.copy import (
    SnapshotAlreadyExistsError,
    SnapshotNotFoundError,
    copy_snapshot,
)


@click.group("copy")
def copy_cmd():
    """Copy (duplicate) a snapshot."""


@copy_cmd.command("run")
@click.argument("source")
@click.argument("destination")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite the destination snapshot if it already exists.",
)
def copy_run_cmd(source: str, destination: str, overwrite: bool) -> None:
    """Copy SOURCE snapshot to DESTINATION."""
    try:
        copy_snapshot(source, destination, overwrite=overwrite)
        click.echo(
            f"Snapshot '{source}' copied to '{destination}' successfully."
        )
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except SnapshotAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
