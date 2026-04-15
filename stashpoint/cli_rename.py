"""CLI commands for renaming snapshots."""

import click
from stashpoint.rename import rename_snapshot, SnapshotNotFoundError, SnapshotAlreadyExistsError


@click.group("rename")
def rename_cmd():
    """Rename a snapshot."""


def _handle_rename_error(e: Exception) -> None:
    """Print an error message to stderr and exit with code 1."""
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(1)


@rename_cmd.command("run")
@click.argument("old_name")
@click.argument("new_name")
def rename_run_cmd(old_name: str, new_name: str):
    """Rename snapshot OLD_NAME to NEW_NAME."""
    try:
        rename_snapshot(old_name, new_name)
        click.echo(f"Snapshot '{old_name}' renamed to '{new_name}'.")
    except SnapshotNotFoundError as e:
        _handle_rename_error(e)
    except SnapshotAlreadyExistsError as e:
        _handle_rename_error(e)
