"""CLI commands for snapshot locking."""

import click

from stashpoint.lock import (
    SnapshotAlreadyLockedError,
    SnapshotNotFoundError,
    SnapshotNotLockedError,
    get_locked_snapshots,
    is_locked,
    lock_snapshot,
    unlock_snapshot,
)


@click.group("lock")
def lock_cmd():
    """Manage snapshot locks."""


@lock_cmd.command("add")
@click.argument("name")
def lock_add_cmd(name: str):
    """Lock a snapshot to prevent modification."""
    try:
        lock_snapshot(name)
        click.echo(f"Snapshot '{name}' is now locked.")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except SnapshotAlreadyLockedError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lock_cmd.command("remove")
@click.argument("name")
def lock_remove_cmd(name: str):
    """Unlock a snapshot."""
    try:
        unlock_snapshot(name)
        click.echo(f"Snapshot '{name}' has been unlocked.")
    except SnapshotNotLockedError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@lock_cmd.command("list")
def lock_list_cmd():
    """List all locked snapshots."""
    locked = get_locked_snapshots()
    if not locked:
        click.echo("No snapshots are currently locked.")
    else:
        click.echo("Locked snapshots:")
        for name in locked:
            click.echo(f"  🔒 {name}")


@lock_cmd.command("check")
@click.argument("name")
def lock_check_cmd(name: str):
    """Check whether a snapshot is locked."""
    if is_locked(name):
        click.echo(f"Snapshot '{name}' is locked.")
    else:
        click.echo(f"Snapshot '{name}' is not locked.")
