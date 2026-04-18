"""CLI commands for snapshot aliases."""

import click
from stashpoint.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    SnapshotNotFoundError,
    AliasNotFoundError,
)


@click.group("alias")
def alias_cmd():
    """Manage snapshot aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("snapshot")
def alias_set_cmd(alias, snapshot):
    """Assign ALIAS to SNAPSHOT."""
    try:
        set_alias(alias, snapshot)
        click.echo(f"Alias '{alias}' -> '{snapshot}' saved.")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: snapshot '{e}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias")
def alias_remove_cmd(alias):
    """Remove an alias."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasNotFoundError as e:
        click.echo(f"Error: alias '{e}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("resolve")
@click.argument("alias")
def alias_resolve_cmd(alias):
    """Print the snapshot name for ALIAS."""
    try:
        name = resolve_alias(alias)
        click.echo(name)
    except AliasNotFoundError as e:
        click.echo(f"Error: alias '{e}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("list")
def alias_list_cmd():
    """List all aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, snapshot in sorted(aliases.items()):
        click.echo(f"{alias} -> {snapshot}")
