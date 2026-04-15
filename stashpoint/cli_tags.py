"""CLI commands for snapshot tag management."""

from __future__ import annotations

import click

from stashpoint.tags import SnapshotNotFoundError, add_tag, get_tags, list_by_tag, remove_tag


@click.group("tag")
def tag_cmd() -> None:
    """Manage tags on snapshots."""


@tag_cmd.command("add")
@click.argument("snapshot")
@click.argument("tag")
def tag_add_cmd(snapshot: str, tag: str) -> None:
    """Add TAG to SNAPSHOT."""
    try:
        updated = add_tag(snapshot, tag)
        click.echo(f"Tagged '{snapshot}' with '{tag}'. Current tags: {', '.join(updated)}")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_cmd.command("remove")
@click.argument("snapshot")
@click.argument("tag")
def tag_remove_cmd(snapshot: str, tag: str) -> None:
    """Remove TAG from SNAPSHOT."""
    updated = remove_tag(snapshot, tag)
    remaining = ", ".join(updated) if updated else "(none)"
    click.echo(f"Removed tag '{tag}' from '{snapshot}'. Remaining tags: {remaining}")


@tag_cmd.command("list")
@click.argument("snapshot")
def tag_list_cmd(snapshot: str) -> None:
    """List all tags on SNAPSHOT."""
    tags = get_tags(snapshot)
    if tags:
        click.echo("  ".join(tags))
    else:
        click.echo(f"No tags on '{snapshot}'.")


@tag_cmd.command("filter")
@click.argument("tag")
def tag_filter_cmd(tag: str) -> None:
    """List all snapshots that carry TAG."""
    names = list_by_tag(tag)
    if names:
        for name in names:
            click.echo(name)
    else:
        click.echo(f"No snapshots found with tag '{tag}'.")
