"""CLI commands for snapshot metadata management."""

import click

from stashpoint.metadata import (
    MetadataKeyNotFoundError,
    SnapshotNotFoundError,
    get_all_metadata,
    get_metadata,
    remove_metadata,
    set_metadata,
)


@click.group("metadata")
def metadata_cmd():
    """Manage arbitrary metadata on snapshots."""


@metadata_cmd.command("set")
@click.argument("snapshot")
@click.argument("key")
@click.argument("value")
def metadata_set_cmd(snapshot: str, key: str, value: str):
    """Set a metadata KEY=VALUE on SNAPSHOT."""
    try:
        result = set_metadata(snapshot, key, value)
        click.echo(f"Metadata set on '{snapshot}': {key}={result[key]!r}")
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)


@metadata_cmd.command("get")
@click.argument("snapshot")
@click.argument("key")
def metadata_get_cmd(snapshot: str, key: str):
    """Get a single metadata KEY from SNAPSHOT."""
    try:
        value = get_metadata(snapshot, key)
        click.echo(str(value))
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)
    except MetadataKeyNotFoundError:
        click.echo(f"Error: metadata key '{key}' not found on '{snapshot}'.", err=True)
        raise SystemExit(1)


@metadata_cmd.command("remove")
@click.argument("snapshot")
@click.argument("key")
def metadata_remove_cmd(snapshot: str, key: str):
    """Remove a metadata KEY from SNAPSHOT."""
    try:
        remove_metadata(snapshot, key)
        click.echo(f"Metadata key '{key}' removed from '{snapshot}'.")
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)
    except MetadataKeyNotFoundError:
        click.echo(f"Error: metadata key '{key}' not found on '{snapshot}'.", err=True)
        raise SystemExit(1)


@metadata_cmd.command("show")
@click.argument("snapshot")
def metadata_show_cmd(snapshot: str):
    """Show all metadata for SNAPSHOT."""
    try:
        data = get_all_metadata(snapshot)
    except SnapshotNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)

    if not data:
        click.echo(f"No metadata set on '{snapshot}'.")
        return
    for key, value in sorted(data.items()):
        click.echo(f"  {key}: {value!r}")
