"""CLI commands for snapshot notes."""

from __future__ import annotations

import click

from stashpoint.notes import SnapshotNotFoundError, get_note, list_notes, remove_note, set_note


@click.group("notes")
def notes_cmd():
    """Manage notes attached to snapshots."""


@notes_cmd.command("set")
@click.argument("name")
@click.argument("text")
def notes_set_cmd(name: str, text: str):
    """Attach a note to a snapshot."""
    try:
        set_note(name, text)
        click.echo(f"Note set for '{name}'.")
    except SnapshotNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@notes_cmd.command("get")
@click.argument("name")
def notes_get_cmd(name: str):
    """Print the note attached to a snapshot."""
    note = get_note(name)
    if note is None:
        click.echo(f"No note set for '{name}'.")
    else:
        click.echo(note)


@notes_cmd.command("remove")
@click.argument("name")
def notes_remove_cmd(name: str):
    """Remove the note attached to a snapshot."""
    remove_note(name)
    click.echo(f"Note removed for '{name}'.")


@notes_cmd.command("list")
def notes_list_cmd():
    """List all snapshot notes."""
    notes = list_notes()
    if not notes:
        click.echo("No notes found.")
        return
    for snap, text in notes.items():
        click.echo(f"{snap}: {text}")
