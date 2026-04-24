"""Module for managing human-readable descriptions attached to snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


def _get_descriptions_path() -> Path:
    return get_stash_path() / "descriptions.json"


def _load_descriptions() -> dict[str, str]:
    path = _get_descriptions_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_descriptions(data: dict[str, str]) -> None:
    path = _get_descriptions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_description(snapshot_name: str, text: str) -> str:
    """Attach a description to a snapshot. Returns the stored text."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_descriptions()
    data[snapshot_name] = text
    _save_descriptions(data)
    return text


def get_description(snapshot_name: str) -> Optional[str]:
    """Return the description for a snapshot, or None if not set."""
    return _load_descriptions().get(snapshot_name)


def remove_description(snapshot_name: str) -> None:
    """Remove the description for a snapshot. No-op if not set."""
    data = _load_descriptions()
    data.pop(snapshot_name, None)
    _save_descriptions(data)


def list_descriptions() -> dict[str, str]:
    """Return all snapshot descriptions keyed by snapshot name."""
    return dict(_load_descriptions())
