"""CLI commands for snapshot versioning."""

from __future__ import annotations

import click
from stashpoint.version import (
    SnapshotNotFoundError,
    VersionNotFoundError,
    create_version,
    list_versions,
    get_version,
    restore_version,
    delete_version,
)


@click.group("version")
def version_cmd():
    """Manage numbered versions of a snapshot."""


@version_cmd.command("create")
@click.argument("snapshot")
@click.option("-m", "--message", default="", help="Optional version message.")
def version_create_cmd(snapshot: str, message: str):
    """Create a new version of SNAPSHOT."""
    try:
        entry = create_version(snapshot, message)
        click.echo(f"Created version {entry['version']} of '{snapshot}'.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@version_cmd.command("list")
@click.argument("snapshot")
def version_list_cmd(snapshot: str):
    """List all versions of SNAPSHOT."""
    entries = list_versions(snapshot)
    if not entries:
        click.echo(f"No versions found for '{snapshot}'.")
        return
    for e in entries:
        ts = click.style(str(round(e['timestamp'])), fg="cyan")
        msg = f"  {e['message']}" if e["message"] else ""
        click.echo(f"v{e['version']}  [{ts}]{msg}")


@version_cmd.command("show")
@click.argument("snapshot")
@click.argument("version", type=int)
def version_show_cmd(snapshot: str, version: int):
    """Show vars stored in a specific VERSION of SNAPSHOT."""
    try:
        entry = get_version(snapshot, version)
    except VersionNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    for k, v in sorted(entry["vars"].items()):
        click.echo(f"{k}={v}")


@version_cmd.command("restore")
@click.argument("snapshot")
@click.argument("version", type=int)
def version_restore_cmd(snapshot: str, version: int):
    """Restore SNAPSHOT to a specific VERSION."""
    try:
        entry = restore_version(snapshot, version)
        click.echo(f"Restored '{snapshot}' to version {entry['version']}.")
    except (SnapshotNotFoundError, VersionNotFoundError) as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@version_cmd.command("delete")
@click.argument("snapshot")
@click.argument("version", type=int)
def version_delete_cmd(snapshot: str, version: int):
    """Delete a specific VERSION of SNAPSHOT."""
    try:
        remaining = delete_version(snapshot, version)
        click.echo(
            f"Deleted version {version} of '{snapshot}'. "
            f"{len(remaining)} version(s) remaining."
        )
    except VersionNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
