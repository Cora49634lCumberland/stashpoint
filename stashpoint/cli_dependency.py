"""CLI commands for snapshot dependency management."""

from __future__ import annotations

import click

from stashpoint.dependency import (
    CircularDependencyError,
    DependencyAlreadyExistsError,
    DependencyNotFoundError,
    SnapshotNotFoundError,
    add_dependency,
    get_dependencies,
    get_dependents,
    remove_dependency,
)


@click.group("dependency", help="Manage snapshot dependencies.")
def dependency_cmd() -> None:
    pass


@dependency_cmd.command("add")
@click.argument("name")
@click.argument("depends_on")
def dependency_add_cmd(name: str, depends_on: str) -> None:
    """Declare that NAME depends on DEPENDS_ON."""
    try:
        deps = add_dependency(name, depends_on)
        click.echo(f"Added dependency: {name} -> {depends_on}")
        click.echo(f"Dependencies of '{name}': {', '.join(deps) or 'none'}")
    except SnapshotNotFoundError as exc:
        click.echo(f"Error: snapshot '{exc}' not found.", err=True)
        raise SystemExit(1)
    except DependencyAlreadyExistsError:
        click.echo(f"Error: '{depends_on}' is already a dependency of '{name}'.", err=True)
        raise SystemExit(1)
    except CircularDependencyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@dependency_cmd.command("remove")
@click.argument("name")
@click.argument("depends_on")
def dependency_remove_cmd(name: str, depends_on: str) -> None:
    """Remove a dependency from NAME."""
    try:
        deps = remove_dependency(name, depends_on)
        click.echo(f"Removed dependency: {name} -> {depends_on}")
        click.echo(f"Remaining dependencies: {', '.join(deps) or 'none'}")
    except DependencyNotFoundError:
        click.echo(f"Error: '{depends_on}' is not a dependency of '{name}'.", err=True)
        raise SystemExit(1)


@dependency_cmd.command("list")
@click.argument("name")
def dependency_list_cmd(name: str) -> None:
    """List direct dependencies of NAME."""
    deps = get_dependencies(name)
    if not deps:
        click.echo(f"'{name}' has no dependencies.")
    else:
        click.echo(f"Dependencies of '{name}':")
        for dep in deps:
            click.echo(f"  - {dep}")


@dependency_cmd.command("dependents")
@click.argument("name")
def dependency_dependents_cmd(name: str) -> None:
    """List snapshots that depend on NAME."""
    dependents = get_dependents(name)
    if not dependents:
        click.echo(f"No snapshots depend on '{name}'.")
    else:
        click.echo(f"Snapshots that depend on '{name}':")
        for dep in dependents:
            click.echo(f"  - {dep}")
