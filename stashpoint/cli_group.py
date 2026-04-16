"""CLI commands for snapshot groups."""

import click
from stashpoint.group import (
    create_group, delete_group, get_group, list_groups, add_to_group,
    GroupNotFoundError, GroupAlreadyExistsError, SnapshotNotFoundError,
)


@click.group("group")
def group_cmd():
    """Manage snapshot groups."""


@group_cmd.command("create")
@click.argument("name")
@click.argument("snapshots", nargs=-1, required=True)
def group_create_cmd(name, snapshots):
    """Create a group with the given snapshots."""
    try:
        members = create_group(name, list(snapshots))
        click.echo(f"Group '{name}' created with: {', '.join(members)}")
    except GroupAlreadyExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("name")
def group_delete_cmd(name):
    """Delete a group."""
    try:
        delete_group(name)
        click.echo(f"Group '{name}' deleted.")
    except GroupNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("show")
@click.argument("name")
def group_show_cmd(name):
    """Show snapshots in a group."""
    try:
        members = get_group(name)
        click.echo(f"Group '{name}':")
        for m in members:
            click.echo(f"  - {m}")
    except GroupNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
def group_list_cmd():
    """List all groups."""
    groups = list_groups()
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in groups.items():
        click.echo(f"{name}: {', '.join(members)}")


@group_cmd.command("add")
@click.argument("group_name")
@click.argument("snapshot_name")
def group_add_cmd(group_name, snapshot_name):
    """Add a snapshot to an existing group."""
    try:
        members = add_to_group(group_name, snapshot_name)
        click.echo(f"Group '{group_name}' now contains: {', '.join(members)}")
    except (GroupNotFoundError, SnapshotNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
