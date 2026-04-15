"""Pin management for stashpoint snapshots.

Allows users to mark snapshots as 'pinned' so they are protected
from accidental deletion or overwrite.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyPinnedError(Exception):
    pass


def _get_pins_path() -> Path:
    return get_stash_path() / "pins.json"


def _load_pins() -> List[str]:
    path = _get_pins_path()
    if not path.exists():
        return []
    with path.open("r") as f:
        return json.load(f)


def _save_pins(pins: List[str]) -> None:
    path = _get_pins_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(pins, f, indent=2)


def pin_snapshot(name: str) -> List[str]:
    """Mark a snapshot as pinned. Raises if snapshot does not exist."""
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    pins = _load_pins()
    if name not in pins:
        pins.append(name)
        _save_pins(pins)
    return pins


def unpin_snapshot(name: str) -> List[str]:
    """Remove pin from a snapshot. Raises if snapshot does not exist."""
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    pins = _load_pins()
    pins = [p for p in pins if p != name]
    _save_pins(pins)
    return pins


def is_pinned(name: str) -> bool:
    """Return True if the snapshot is pinned."""
    return name in _load_pins()


def get_pinned() -> List[str]:
    """Return all pinned snapshot names."""
    return _load_pins()
