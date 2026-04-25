"""CLI commands for managing snapshot annotations."""

from __future__ import annotations

import click

from stashpoint.annotation import (
    AnnotationKeyNotFoundError,
    SnapshotNotFoundError,
    get_all_annotations,
    get_annotation,
    list_annotated_snapshots,
    remove_annotation,
    set_annotation,
)


@click.group("annotation")
def annotation_cmd() -> None:
    """Manage inline key-value annotations on snapshots."""


@annotation_cmd.command("set")
@click.argument("snapshot")
@click.argument("key")
@click.argument("value")
def annotation_set_cmd(snapshot: str, key: str, value: str) -> None:
    """Set an annotation KEY=VALUE on SNAPSHOT."""
    try:
        annotations = set_annotation(snapshot, key, value)
        click.echo(f"Annotation set on '{snapshot}': {key}={value!r}")
        for k, v in annotations.items():
            click.echo(f"  {k}: {v}")
    except SnapshotNotFoundError as exc:
        raise click.ClickException(str(exc))


@annotation_cmd.command("get")
@click.argument("snapshot")
@click.argument("key")
def annotation_get_cmd(snapshot: str, key: str) -> None:
    """Get the value of annotation KEY on SNAPSHOT."""
    value = get_annotation(snapshot, key)
    if value is None:
        raise click.ClickException(
            f"Annotation key '{key}' not found on snapshot '{snapshot}'."
        )
    click.echo(value)


@annotation_cmd.command("remove")
@click.argument("snapshot")
@click.argument("key")
def annotation_remove_cmd(snapshot: str, key: str) -> None:
    """Remove annotation KEY from SNAPSHOT."""
    try:
        remove_annotation(snapshot, key)
        click.echo(f"Removed annotation '{key}' from '{snapshot}'.")
    except (SnapshotNotFoundError, AnnotationKeyNotFoundError) as exc:
        raise click.ClickException(str(exc))


@annotation_cmd.command("show")
@click.argument("snapshot")
def annotation_show_cmd(snapshot: str) -> None:
    """Show all annotations for SNAPSHOT."""
    annotations = get_all_annotations(snapshot)
    if not annotations:
        click.echo(f"No annotations for '{snapshot}'.")
        return
    for k, v in annotations.items():
        click.echo(f"  {k}: {v}")


@annotation_cmd.command("list")
def annotation_list_cmd() -> None:
    """List all snapshots that have annotations."""
    data = list_annotated_snapshots()
    if not data:
        click.echo("No annotated snapshots.")
        return
    for snap, annotations in data.items():
        click.echo(f"{snap}:")
        for k, v in annotations.items():
            click.echo(f"  {k}: {v}")
