"""Snapshot index: build and query a searchable index of all snapshot keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import get_stash_path, load_snapshots


class SnapshotNotFoundError(Exception):
    pass


def _get_index_path() -> Path:
    return get_stash_path() / "snapshot_index.json"


def _load_index() -> Dict[str, List[str]]:
    path = _get_index_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_index(index: Dict[str, List[str]]) -> None:
    path = _get_index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2))


def build_index() -> Dict[str, List[str]]:
    """Build an index mapping each env key to the list of snapshots that contain it."""
    snapshots = load_snapshots()
    index: Dict[str, List[str]] = {}
    for name, env in snapshots.items():
        for key in env:
            index.setdefault(key, [])
            if name not in index[key]:
                index[key].append(name)
    _save_index(index)
    return index


def get_index() -> Dict[str, List[str]]:
    """Return the cached index, or build it if not present."""
    path = _get_index_path()
    if not path.exists():
        return build_index()
    return _load_index()


def snapshots_containing_key(key: str) -> List[str]:
    """Return snapshot names that contain the given environment key."""
    index = get_index()
    return index.get(key, [])


def keys_in_snapshot(name: str) -> List[str]:
    """Return all env keys recorded in the index for a given snapshot name."""
    snapshots = load_snapshots()
    if name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    return list(snapshots[name].keys())


def invalidate_index() -> None:
    """Remove the cached index so it will be rebuilt on next access."""
    path = _get_index_path()
    if path.exists():
        path.unlink()
