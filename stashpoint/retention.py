"""Retention policy management for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshots


class SnapshotNotFoundError(Exception):
    pass


class InvalidRetentionError(Exception):
    pass


VALID_POLICIES = ("keep_last", "keep_days", "keep_all")


def _get_retention_path() -> Path:
    return get_stash_path() / "retention.json"


def _load_retention() -> dict:
    path = _get_retention_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_retention(data: dict) -> None:
    path = _get_retention_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_retention(snapshot_name: str, policy: str, value: Optional[int] = None) -> dict:
    """Set a retention policy on a snapshot."""
    snapshots = load_snapshots()
    if snapshot_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    if policy not in VALID_POLICIES:
        raise InvalidRetentionError(
            f"Invalid policy '{policy}'. Must be one of: {', '.join(VALID_POLICIES)}"
        )
    if policy in ("keep_last", "keep_days") and (value is None or value < 1):
        raise InvalidRetentionError(
            f"Policy '{policy}' requires a positive integer value."
        )
    data = _load_retention()
    entry = {"policy": policy}
    if value is not None:
        entry["value"] = value
    data[snapshot_name] = entry
    _save_retention(data)
    return entry


def get_retention(snapshot_name: str) -> Optional[dict]:
    """Get the retention policy for a snapshot, or None if not set."""
    data = _load_retention()
    return data.get(snapshot_name)


def remove_retention(snapshot_name: str) -> None:
    """Remove the retention policy for a snapshot."""
    data = _load_retention()
    if snapshot_name in data:
        del data[snapshot_name]
        _save_retention(data)


def list_retention() -> dict:
    """Return all retention policies keyed by snapshot name."""
    return _load_retention()
