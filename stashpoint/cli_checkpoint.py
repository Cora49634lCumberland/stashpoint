"""CLI commands for checkpoint management."""

from __future__ import annotations

import click

from stashpoint.checkpoint import (
    CheckpointAlreadyExistsError,
    CheckpointNotFoundError,
    SnapshotNotFoundError,
    create_checkpoint,
    get_checkpoints,
    remove_checkpoint,
)


@click.group("checkpoint")
def checkpoint_cmd():
    """Manage snapshot checkpoints."""


@checkpoint_cmd.command("add")
@click.argument("snapshot")
@click.argument("name")
def checkpoint_add_cmd(snapshot: str, name: str):
    """Create a checkpoint NAME for SNAPSHOT."""
    try:
        entry = create_checkpoint(snapshot, name)
        click.echo(
            f"Checkpoint '{entry['checkpoint']}' created for '{entry['snapshot']}' "
            f"at {entry['created_at']:.0f}."
        )
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except CheckpointAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@checkpoint_cmd.command("remove")
@click.argument("snapshot")
@click.argument("name")
def checkpoint_remove_cmd(snapshot: str, name: str):
    """Remove checkpoint NAME from SNAPSHOT."""
    try:
        remove_checkpoint(snapshot, name)
        click.echo(f"Checkpoint '{name}' removed from '{snapshot}'.")
    except CheckpointNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@checkpoint_cmd.command("list")
@click.argument("snapshot")
def checkpoint_list_cmd(snapshot: str):
    """List all checkpoints for SNAPSHOT."""
    entries = get_checkpoints(snapshot)
    if not entries:
        click.echo(f"No checkpoints for '{snapshot}'.")
        return
    for entry in entries:
        click.echo(f"  {entry['checkpoint']}  (created: {entry['created_at']:.0f})")
