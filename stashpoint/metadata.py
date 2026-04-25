"""Snapshot metadata: attach arbitrary key-value metadata to snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class MetadataKeyNotFoundError(Exception):
    pass


def _get_metadata_path() -> Path:
    return get_stash_path() / "metadata.json"


def _load_metadata() -> dict[str, dict[str, Any]]:
    path = _get_metadata_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_metadata(data: dict[str, dict[str, Any]]) -> None:
    path = _get_metadata_path()
    path.write_text(json.dumps(data, indent=2))


def set_metadata(snapshot_name: str, key: str, value: Any) -> dict[str, Any]:
    """Set a metadata key on a snapshot. Returns the full metadata dict."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    data = _load_metadata()
    data.setdefault(snapshot_name, {})
    data[snapshot_name][key] = value
    _save_metadata(data)
    return dict(data[snapshot_name])


def get_metadata(snapshot_name: str, key: str) -> Any:
    """Get a single metadata value. Raises MetadataKeyNotFoundError if absent."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    data = _load_metadata()
    entry = data.get(snapshot_name, {})
    if key not in entry:
        raise MetadataKeyNotFoundError(key)
    return entry[key]


def remove_metadata(snapshot_name: str, key: str) -> dict[str, Any]:
    """Remove a metadata key. Raises MetadataKeyNotFoundError if absent."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    data = _load_metadata()
    entry = data.get(snapshot_name, {})
    if key not in entry:
        raise MetadataKeyNotFoundError(key)
    del entry[key]
    data[snapshot_name] = entry
    _save_metadata(data)
    return dict(entry)


def get_all_metadata(snapshot_name: str) -> dict[str, Any]:
    """Return all metadata for a snapshot (empty dict if none set)."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    data = _load_metadata()
    return dict(data.get(snapshot_name, {}))
