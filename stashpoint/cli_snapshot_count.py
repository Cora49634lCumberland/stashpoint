"""CLI commands for snapshot restore-count tracking."""

from __future__ import annotations

import click

from stashpoint.snapshot_count import (
    SnapshotNotFoundError,
    get_count,
    increment_count,
    list_counts,
    reset_count,
)


@click.group("count")
def count_cmd() -> None:
    """Track how many times snapshots have been restored."""


@count_cmd.command("get")
@click.argument("name")
def count_get_cmd(name: str) -> None:
    """Show the restore count for a snapshot."""
    try:
        value = get_count(name)
        click.echo(f"{name}: {value}")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@count_cmd.command("increment")
@click.argument("name")
def count_increment_cmd(name: str) -> None:
    """Manually increment the restore count for a snapshot."""
    try:
        new_count = increment_count(name)
        click.echo(f"Count for '{name}' is now {new_count}.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@count_cmd.command("reset")
@click.argument("name")
def count_reset_cmd(name: str) -> None:
    """Reset the restore count for a snapshot to zero."""
    try:
        reset_count(name)
        click.echo(f"Count for '{name}' reset to 0.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@count_cmd.command("list")
def count_list_cmd() -> None:
    """List all snapshots with their restore counts."""
    entries = list_counts()
    if not entries:
        click.echo("No count data recorded yet.")
        return
    for entry in entries:
        click.echo(f"{entry['name']}: {entry['count']}")
