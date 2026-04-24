"""Access control for snapshots: restrict read/write by user or role."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import get_stash_path, load_snapshots


class SnapshotNotFoundError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class AccessEntryNotFoundError(Exception):
    pass


def _get_access_path() -> Path:
    return get_stash_path() / "access.json"


def _load_access() -> Dict[str, Dict[str, List[str]]]:
    path = _get_access_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_access(data: Dict[str, Dict[str, List[str]]]) -> None:
    path = _get_access_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_access(snapshot_name: str, principal: str, permissions: List[str]) -> Dict[str, List[str]]:
    """Set access permissions for a principal on a snapshot.
    permissions: list of 'read', 'write'
    """
    snapshots = load_snapshots()
    if snapshot_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")

    valid = {"read", "write"}
    permissions = [p for p in permissions if p in valid]

    data = _load_access()
    if snapshot_name not in data:
        data[snapshot_name] = {}
    data[snapshot_name][principal] = permissions
    _save_access(data)
    return data[snapshot_name]


def remove_access(snapshot_name: str, principal: str) -> Dict[str, List[str]]:
    """Remove access entry for a principal on a snapshot."""
    data = _load_access()
    if snapshot_name not in data or principal not in data[snapshot_name]:
        raise AccessEntryNotFoundError(
            f"No access entry for '{principal}' on snapshot '{snapshot_name}'."
        )
    del data[snapshot_name][principal]
    _save_access(data)
    return data.get(snapshot_name, {})


def get_access(snapshot_name: str) -> Dict[str, List[str]]:
    """Return all access entries for a snapshot."""
    data = _load_access()
    return data.get(snapshot_name, {})


def check_access(snapshot_name: str, principal: str, permission: str) -> bool:
    """Return True if principal has the given permission on the snapshot."""
    data = _load_access()
    perms = data.get(snapshot_name, {}).get(principal, [])
    return permission in perms
