"""Attach and retrieve text notes on named snapshots."""

from __future__ import annotations

import json
from pathlib import Path

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


def _get_notes_path() -> Path:
    return get_stash_path() / "notes.json"


def _load_notes() -> dict[str, str]:
    path = _get_notes_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_notes(notes: dict[str, str]) -> None:
    _get_notes_path().write_text(json.dumps(notes, indent=2))


def set_note(name: str, text: str) -> str:
    """Attach *text* as the note for snapshot *name*. Returns the note."""
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    notes = _load_notes()
    notes[name] = text
    _save_notes(notes)
    return text


def get_note(name: str) -> str | None:
    """Return the note for *name*, or None if none is set."""
    return _load_notes().get(name)


def remove_note(name: str) -> None:
    """Remove the note for *name* if present."""
    notes = _load_notes()
    notes.pop(name, None)
    _save_notes(notes)


def list_notes() -> dict[str, str]:
    """Return all snapshot notes."""
    return _load_notes()
