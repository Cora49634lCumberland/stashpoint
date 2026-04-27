"""Track and report the size (number of keys) of snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(KeyError):
    pass


def _get_sizes_path() -> Path:
    return get_stash_path() / "snapshot_sizes.json"


def _load_sizes() -> dict:
    path = _get_sizes_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_sizes(sizes: dict) -> None:
    path = _get_sizes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(sizes, f, indent=2)


def compute_size(name: str) -> int:
    """Compute and cache the number of keys in a snapshot."""
    data = load_snapshot(name)
    if data is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    size = len(data)
    sizes = _load_sizes()
    sizes[name] = size
    _save_sizes(sizes)
    return size


def get_size(name: str) -> Optional[int]:
    """Return the cached size for a snapshot, or None if not yet computed."""
    return _load_sizes().get(name)


def remove_size(name: str) -> None:
    """Remove cached size entry for a snapshot."""
    sizes = _load_sizes()
    sizes.pop(name, None)
    _save_sizes(sizes)


def list_sizes() -> dict[str, int]:
    """Return all cached snapshot sizes, sorted by size descending."""
    sizes = _load_sizes()
    return dict(sorted(sizes.items(), key=lambda item: item[1], reverse=True))
