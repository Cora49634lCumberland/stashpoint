"""CLI commands for namespace management."""

import click
from stashpoint.namespace import (
    create_namespace,
    delete_namespace,
    add_to_namespace,
    remove_from_namespace,
    list_namespaces,
    get_namespace,
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    SnapshotNotFoundError,
)


@click.group("namespace")
def namespace_cmd():
    """Manage snapshot namespaces."""


@namespace_cmd.command("create")
@click.argument("name")
def namespace_create_cmd(name):
    """Create a new namespace."""
    try:
        create_namespace(name)
        click.echo(f"Namespace '{name}' created.")
    except NamespaceAlreadyExistsError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("delete")
@click.argument("name")
def namespace_delete_cmd(name):
    """Delete a namespace."""
    try:
        delete_namespace(name)
        click.echo(f"Namespace '{name}' deleted.")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("add")
@click.argument("namespace")
@click.argument("snapshot")
def namespace_add_cmd(namespace, snapshot):
    """Add a snapshot to a namespace."""
    try:
        members = add_to_namespace(namespace, snapshot)
        click.echo(f"Snapshot '{snapshot}' added to '{namespace}'. Members: {members}")
    except (NamespaceNotFoundError, SnapshotNotFoundError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("remove")
@click.argument("namespace")
@click.argument("snapshot")
def namespace_remove_cmd(namespace, snapshot):
    """Remove a snapshot from a namespace."""
    try:
        members = remove_from_namespace(namespace, snapshot)
        click.echo(f"Snapshot '{snapshot}' removed from '{namespace}'. Members: {members}")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@namespace_cmd.command("list")
def namespace_list_cmd():
    """List all namespaces."""
    data = list_namespaces()
    if not data:
        click.echo("No namespaces defined.")
        return
    for name, members in data.items():
        click.echo(f"{name}: {', '.join(members) if members else '(empty)'}")


@namespace_cmd.command("show")
@click.argument("name")
def namespace_show_cmd(name):
    """Show members of a namespace."""
    try:
        members = get_namespace(name)
        click.echo(f"Namespace '{name}': {members}")
    except NamespaceNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
