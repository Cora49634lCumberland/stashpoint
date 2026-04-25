"""CLI commands for snapshot trigger management."""

from __future__ import annotations

import click

from stashpoint.trigger import (
    SnapshotNotFoundError,
    TriggerNotFoundError,
    list_triggers,
    remove_trigger,
    resolve_trigger,
    set_trigger,
)


@click.group("trigger")
def trigger_cmd() -> None:
    """Manage snapshot triggers."""


@trigger_cmd.command("set")
@click.argument("trigger_name")
@click.argument("snapshot_name")
def trigger_set_cmd(trigger_name: str, snapshot_name: str) -> None:
    """Bind TRIGGER_NAME to SNAPSHOT_NAME."""
    try:
        result = set_trigger(trigger_name, snapshot_name)
        click.echo(f"Trigger '{trigger_name}' -> '{result}'")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trigger_cmd.command("remove")
@click.argument("trigger_name")
def trigger_remove_cmd(trigger_name: str) -> None:
    """Remove a trigger binding."""
    try:
        remove_trigger(trigger_name)
        click.echo(f"Trigger '{trigger_name}' removed.")
    except TriggerNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trigger_cmd.command("resolve")
@click.argument("trigger_name")
def trigger_resolve_cmd(trigger_name: str) -> None:
    """Print the snapshot bound to TRIGGER_NAME."""
    snapshot = resolve_trigger(trigger_name)
    if snapshot is None:
        click.echo(f"No snapshot bound to trigger '{trigger_name}'.", err=True)
        raise SystemExit(1)
    click.echo(snapshot)


@trigger_cmd.command("list")
def trigger_list_cmd() -> None:
    """List all trigger bindings."""
    entries = list_triggers()
    if not entries:
        click.echo("No triggers defined.")
        return
    for entry in entries:
        click.echo(f"{entry['trigger']:30s}  {entry['snapshot']}")
