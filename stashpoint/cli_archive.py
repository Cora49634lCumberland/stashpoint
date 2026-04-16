"""CLI commands for archiving and unarchiving snapshots."""

import click
from stashpoint.archive import (
    archive_snapshot,
    unarchive_snapshot,
    list_archived,
    purge_snapshot,
    SnapshotNotFoundError,
    SnapshotAlreadyArchivedError,
    SnapshotNotArchivedError,
)


@click.group("archive")
def archive_cmd():
    """Manage archived (soft-deleted) snapshots."""


@archive_cmd.command("add")
@click.argument("name")
def archive_add_cmd(name):
    """Archive a snapshot by NAME."""
    try:
        archive_snapshot(name)
        click.echo(f"Snapshot '{name}' archived.")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except SnapshotAlreadyArchivedError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@archive_cmd.command("restore")
@click.argument("name")
def archive_restore_cmd(name):
    """Restore an archived snapshot by NAME."""
    try:
        unarchive_snapshot(name)
        click.echo(f"Snapshot '{name}' restored from archive.")
    except SnapshotNotArchivedError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@archive_cmd.command("list")
def archive_list_cmd():
    """List all archived snapshots."""
    names = list_archived()
    if not names:
        click.echo("No archived snapshots.")
    else:
        for name in names:
            click.echo(name)


@archive_cmd.command("purge")
@click.argument("name")
@click.confirmation_option(prompt="Permanently delete this archived snapshot?")
def archive_purge_cmd(name):
    """Permanently delete an archived snapshot by NAME."""
    try:
        purge_snapshot(name)
        click.echo(f"Archived snapshot '{name}' permanently deleted.")
    except SnapshotNotArchivedError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
