"""CLI commands for snapshot access control."""

from __future__ import annotations

import click

from stashpoint.access import (
    AccessDeniedError,
    AccessEntryNotFoundError,
    SnapshotNotFoundError,
    check_access,
    get_access,
    remove_access,
    set_access,
)


@click.group("access")
def access_cmd():
    """Manage access control for snapshots."""


@access_cmd.command("set")
@click.argument("snapshot")
@click.argument("principal")
@click.option("--read", "perms", flag_value="read", multiple=False, default=None)
@click.option("--write", "write_flag", is_flag=True, default=False)
@click.option("-p", "--permission", "permissions", multiple=True,
              help="Permission to grant: read or write (repeatable).")
def access_set_cmd(snapshot, principal, perms, write_flag, permissions):
    """Grant permissions to PRINCIPAL on SNAPSHOT."""
    perm_list = list(permissions)
    if perms:
        perm_list.append(perms)
    if write_flag:
        perm_list.append("write")
    if not perm_list:
        perm_list = ["read"]
    try:
        result = set_access(snapshot, principal, perm_list)
        click.echo(f"Access set for '{principal}' on '{snapshot}': {', '.join(result.get(principal, []))}")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@access_cmd.command("remove")
@click.argument("snapshot")
@click.argument("principal")
def access_remove_cmd(snapshot, principal):
    """Remove access entry for PRINCIPAL on SNAPSHOT."""
    try:
        remove_access(snapshot, principal)
        click.echo(f"Access entry for '{principal}' on '{snapshot}' removed.")
    except (AccessEntryNotFoundError, SnapshotNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@access_cmd.command("list")
@click.argument("snapshot")
def access_list_cmd(snapshot):
    """List all access entries for SNAPSHOT."""
    entries = get_access(snapshot)
    if not entries:
        click.echo(f"No access entries for '{snapshot}'.")
        return
    for principal, perms in sorted(entries.items()):
        click.echo(f"  {principal}: {', '.join(perms)}")


@access_cmd.command("check")
@click.argument("snapshot")
@click.argument("principal")
@click.argument("permission")
def access_check_cmd(snapshot, principal, permission):
    """Check if PRINCIPAL has PERMISSION on SNAPSHOT."""
    allowed = check_access(snapshot, principal, permission)
    if allowed:
        click.echo(f"'{principal}' has '{permission}' access on '{snapshot}'.")
    else:
        click.echo(f"'{principal}' does NOT have '{permission}' access on '{snapshot}'.")
        raise SystemExit(1)
