"""CLI commands for cloning snapshots."""

import click
from stashpoint.clone import SnapshotAlreadyExistsError, SnapshotNotFoundError, clone_snapshot


@click.group("clone")
def clone_cmd():
    """Clone snapshots."""


@clone_cmd.command("run")
@click.argument("source")
@click.argument("destination")
@click.option(
    "--keys",
    "-k",
    multiple=True,
    help="Keys to include in the clone (repeatable). Defaults to all keys.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite destination if it already exists.",
)
def clone_run_cmd(source: str, destination: str, keys: tuple, overwrite: bool):
    """Clone SOURCE snapshot into DESTINATION."""
    try:
        result = clone_snapshot(
            source,
            destination,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
        key_count = len(result)
        click.echo(
            f"Cloned '{source}' -> '{destination}' ({key_count} key(s) copied)."
        )
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except SnapshotAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
