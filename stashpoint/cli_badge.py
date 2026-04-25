"""CLI commands for the badge feature."""

from __future__ import annotations

import click

from stashpoint.badge import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    SnapshotNotFoundError,
    add_badge,
    find_by_badge,
    get_badges,
    remove_badge,
)


@click.group("badge")
def badge_cmd() -> None:
    """Manage badges assigned to snapshots."""


@badge_cmd.command("add")
@click.argument("snapshot")
@click.argument("badge")
def badge_add_cmd(snapshot: str, badge: str) -> None:
    """Assign BADGE to SNAPSHOT."""
    try:
        badges = add_badge(snapshot, badge)
        click.echo(f"Badge '{badge}' added to '{snapshot}'. Badges: {', '.join(badges)}")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except BadgeAlreadyExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@badge_cmd.command("remove")
@click.argument("snapshot")
@click.argument("badge")
def badge_remove_cmd(snapshot: str, badge: str) -> None:
    """Remove BADGE from SNAPSHOT."""
    try:
        badges = remove_badge(snapshot, badge)
        remaining = ", ".join(badges) if badges else "(none)"
        click.echo(f"Badge '{badge}' removed from '{snapshot}'. Remaining: {remaining}")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except BadgeNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@badge_cmd.command("list")
@click.argument("snapshot")
def badge_list_cmd(snapshot: str) -> None:
    """List all badges assigned to SNAPSHOT."""
    badges = get_badges(snapshot)
    if badges:
        for b in badges:
            click.echo(b)
    else:
        click.echo(f"No badges assigned to '{snapshot}'.")


@badge_cmd.command("find")
@click.argument("badge")
def badge_find_cmd(badge: str) -> None:
    """Find all snapshots that carry BADGE."""
    names = find_by_badge(badge)
    if names:
        for name in names:
            click.echo(name)
    else:
        click.echo(f"No snapshots found with badge '{badge}'.")
