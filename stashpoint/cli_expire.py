"""CLI commands for snapshot expiry management."""

import click
from stashpoint.expire import (
    SnapshotNotFoundError,
    set_expiry,
    remove_expiry,
    get_expiry,
    list_expiring,
    purge_expired,
)
import time


@click.group("expire")
def expire_cmd():
    """Manage snapshot expiry (TTL)."""


@expire_cmd.command("set")
@click.argument("name")
@click.argument("ttl", type=int)
def expire_set_cmd(name: str, ttl: int):
    """Set a TTL in seconds on snapshot NAME."""
    try:
        expires_at = set_expiry(name, ttl)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at))
        click.echo(f"Snapshot '{name}' will expire at {ts} (in {ttl}s).")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@expire_cmd.command("remove")
@click.argument("name")
def expire_remove_cmd(name: str):
    """Remove the expiry from snapshot NAME."""
    remove_expiry(name)
    click.echo(f"Expiry removed from snapshot '{name}'.")


@expire_cmd.command("check")
@click.argument("name")
def expire_check_cmd(name: str):
    """Check the expiry status of snapshot NAME."""
    ts = get_expiry(name)
    if ts is None:
        click.echo(f"Snapshot '{name}' has no expiry set.")
        return
    remaining = ts - time.time()
    formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    if remaining <= 0:
        click.echo(f"Snapshot '{name}' expired at {formatted}.")
    else:
        click.echo(f"Snapshot '{name}' expires at {formatted} ({int(remaining)}s remaining).")


@expire_cmd.command("list")
def expire_list_cmd():
    """List all snapshots with expiry set."""
    entries = list_expiring()
    if not entries:
        click.echo("No snapshots have expiry set.")
        return
    for entry in entries:
        status = "EXPIRED" if entry["expired"] else f"{int(entry['seconds_remaining'])}s remaining"
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["expires_at"]))
        click.echo(f"  {entry['name']:<20} {ts}  [{status}]")


@expire_cmd.command("purge")
def expire_purge_cmd():
    """Delete all expired snapshots."""
    purged = purge_expired()
    if not purged:
        click.echo("No expired snapshots to purge.")
    else:
        for name in purged:
            click.echo(f"Purged: {name}")
        click.echo(f"{len(purged)} snapshot(s) purged.")
