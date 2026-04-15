"""CLI commands for pinning and unpinning snapshots."""

from __future__ import annotations

import click

from stashpoint.pin import (
    SnapshotNotFoundError,
    get_pinned,
    is_pinned,
    pin_snapshot,
    unpin_snapshot,
)


@click.group("pin")
def pin_cmd() -> None:
    """Manage pinned snapshots."""


@pin_cmd.command("add")
@click.argument("name")
def pin_add_cmd(name: str) -> None:
    """Pin a snapshot to protect it from deletion or overwrite."""
    try:
        pins = pin_snapshot(name)
        click.echo(f"Pinned '{name}'. Pinned snapshots: {', '.join(pins)}")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@pin_cmd.command("remove")
@click.argument("name")
def pin_remove_cmd(name: str) -> None:
    """Unpin a snapshot."""
    try:
        unpin_snapshot(name)
        click.echo(f"Unpinned '{name}'.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@pin_cmd.command("list")
def pin_list_cmd() -> None:
    """List all pinned snapshots."""
    pins = get_pinned()
    if not pins:
        click.echo("No pinned snapshots.")
    else:
        for name in pins:
            click.echo(name)


@pin_cmd.command("check")
@click.argument("name")
def pin_check_cmd(name: str) -> None:
    """Check whether a snapshot is pinned."""
    if is_pinned(name):
        click.echo(f"'{name}' is pinned.")
    else:
        click.echo(f"'{name}' is not pinned.")
