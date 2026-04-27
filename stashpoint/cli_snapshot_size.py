"""CLI commands for snapshot size inspection."""

from __future__ import annotations

import click

from stashpoint.snapshot_size import (
    SnapshotNotFoundError,
    compute_size,
    get_size,
    list_sizes,
    remove_size,
)


@click.group("size")
def size_cmd():
    """Inspect snapshot key counts."""


@size_cmd.command("compute")
@click.argument("name")
def size_compute_cmd(name: str):
    """Compute and cache the size (key count) of a snapshot."""
    try:
        count = compute_size(name)
        click.echo(f"Snapshot '{name}' has {count} key(s).")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@size_cmd.command("get")
@click.argument("name")
def size_get_cmd(name: str):
    """Show the cached size of a snapshot."""
    count = get_size(name)
    if count is None:
        click.echo(f"No cached size for '{name}'. Run 'size compute {name}' first.")
    else:
        click.echo(f"{count}")


@size_cmd.command("remove")
@click.argument("name")
def size_remove_cmd(name: str):
    """Remove the cached size entry for a snapshot."""
    remove_size(name)
    click.echo(f"Removed cached size for '{name}'.")


@size_cmd.command("list")
def size_list_cmd():
    """List all cached snapshot sizes, largest first."""
    sizes = list_sizes()
    if not sizes:
        click.echo("No cached sizes found.")
        return
    for name, count in sizes.items():
        click.echo(f"{name}: {count} key(s)")
