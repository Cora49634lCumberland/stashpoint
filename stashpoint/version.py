"""Snapshot versioning — create, list, and restore numbered versions of a snapshot."""

from __future__ import annotations

import time
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshots, save_snapshots


class SnapshotNotFoundError(Exception):
    pass


class VersionNotFoundError(Exception):
    pass


def _get_versions_path():
    return get_stash_path() / "versions.json"


def _load_versions() -> dict:
    path = _get_versions_path()
    if not path.exists():
        return {}
    import json
    return json.loads(path.read_text())


def _save_versions(data: dict) -> None:
    import json
    path = _get_versions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def create_version(snapshot_name: str, message: str = "") -> dict:
    """Save the current state of a snapshot as a new numbered version."""
    snapshots = load_snapshots()
    if snapshot_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")

    versions = _load_versions()
    history = versions.get(snapshot_name, [])
    next_number = (history[-1]["version"] + 1) if history else 1

    entry = {
        "version": next_number,
        "timestamp": time.time(),
        "message": message,
        "vars": dict(snapshots[snapshot_name]),
    }
    history.append(entry)
    versions[snapshot_name] = history
    _save_versions(versions)
    return entry


def list_versions(snapshot_name: str) -> list[dict]:
    """Return all versions for a snapshot, newest first."""
    versions = _load_versions()
    history = versions.get(snapshot_name, [])
    return list(reversed(history))


def get_version(snapshot_name: str, version_number: int) -> dict:
    """Return a specific version entry."""
    for entry in _load_versions().get(snapshot_name, []):
        if entry["version"] == version_number:
            return entry
    raise VersionNotFoundError(
        f"Version {version_number} of snapshot '{snapshot_name}' not found."
    )


def restore_version(snapshot_name: str, version_number: int) -> dict:
    """Overwrite the active snapshot with the vars from a specific version."""
    entry = get_version(snapshot_name, version_number)
    snapshots = load_snapshots()
    snapshots[snapshot_name] = entry["vars"]
    save_snapshots(snapshots)
    return entry


def delete_version(snapshot_name: str, version_number: int) -> list[dict]:
    """Remove a specific version; returns remaining versions (newest first)."""
    versions = _load_versions()
    history = versions.get(snapshot_name, [])
    updated = [e for e in history if e["version"] != version_number]
    if len(updated) == len(history):
        raise VersionNotFoundError(
            f"Version {version_number} of snapshot '{snapshot_name}' not found."
        )
    versions[snapshot_name] = updated
    _save_versions(versions)
    return list(reversed(updated))
