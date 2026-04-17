"""CLI commands for snapshot labels."""

import click
from stashpoint.label import (
    set_label,
    remove_label,
    resolve_label,
    list_labels,
    SnapshotNotFoundError,
    LabelNotFoundError,
)


@click.group("label")
def label_cmd():
    """Manage snapshot labels."""


@label_cmd.command("set")
@click.argument("label")
@click.argument("snapshot")
def label_set_cmd(label, snapshot):
    """Assign LABEL to SNAPSHOT."""
    try:
        set_label(snapshot, label)
        click.echo(f"Label '{label}' -> '{snapshot}' set.")
    except SnapshotNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_cmd.command("remove")
@click.argument("label")
def label_remove_cmd(label):
    """Remove LABEL."""
    try:
        remove_label(label)
        click.echo(f"Label '{label}' removed.")
    except LabelNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_cmd.command("resolve")
@click.argument("label")
def label_resolve_cmd(label):
    """Print the snapshot name for LABEL."""
    try:
        name = resolve_label(label)
        click.echo(name)
    except LabelNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_cmd.command("list")
def label_list_cmd():
    """List all labels."""
    labels = list_labels()
    if not labels:
        click.echo("No labels defined.")
        return
    for lbl, snap in sorted(labels.items()):
        click.echo(f"{lbl} -> {snap}")
