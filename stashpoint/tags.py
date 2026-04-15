"""Tag management for snapshots — attach, remove, and filter by tags."""

from __future__ import annotations

from typing import Dict, List, Optional

from stashpoint.storage import load_snapshots, save_snapshots

_TAGS_KEY = "__tags__"


class SnapshotNotFoundError(Exception):
    pass


def _load_tags(snapshots: dict) -> Dict[str, List[str]]:
    """Return the tags mapping stored inside the snapshots file."""
    return snapshots.get(_TAGS_KEY, {})


def add_tag(snapshot_name: str, tag: str) -> List[str]:
    """Add *tag* to *snapshot_name*. Returns the updated tag list."""
    snapshots = load_snapshots()
    if snapshot_name not in snapshots and snapshot_name != _TAGS_KEY:
        if snapshot_name not in {k for k in snapshots if k != _TAGS_KEY}:
            raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")

    tags_map: Dict[str, List[str]] = _load_tags(snapshots)
    current = tags_map.get(snapshot_name, [])
    if tag not in current:
        current.append(tag)
    tags_map[snapshot_name] = current
    snapshots[_TAGS_KEY] = tags_map
    save_snapshots(snapshots)
    return current


def remove_tag(snapshot_name: str, tag: str) -> List[str]:
    """Remove *tag* from *snapshot_name*. Returns the updated tag list."""
    snapshots = load_snapshots()
    tags_map: Dict[str, List[str]] = _load_tags(snapshots)
    current = tags_map.get(snapshot_name, [])
    if tag in current:
        current.remove(tag)
    tags_map[snapshot_name] = current
    snapshots[_TAGS_KEY] = tags_map
    save_snapshots(snapshots)
    return current


def get_tags(snapshot_name: str) -> List[str]:
    """Return the list of tags for *snapshot_name*."""
    snapshots = load_snapshots()
    return _load_tags(snapshots).get(snapshot_name, [])


def list_by_tag(tag: str) -> List[str]:
    """Return all snapshot names that carry *tag*."""
    snapshots = load_snapshots()
    tags_map = _load_tags(snapshots)
    return [name for name, tags in tags_map.items() if tag in tags]
