"""Snapshot locking — prevent modification of locked snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashpoint.storage import get_stash_path


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyLockedError(Exception):
    pass


class SnapshotNotLockedError(Exception):
    pass


def _get_locks_path() -> Path:
    return get_stash_path() / "locks.json"


def _load_locks() -> List[str]:
    path = _get_locks_path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_locks(locks: List[str]) -> None:
    _get_locks_path().write_text(json.dumps(locks, indent=2))


def lock_snapshot(name: str) -> List[str]:
    """Lock a snapshot, preventing it from being modified or deleted."""
    from stashpoint.storage import load_snapshot

    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' does not exist.")

    locks = _load_locks()
    if name in locks:
        raise SnapshotAlreadyLockedError(f"Snapshot '{name}' is already locked.")

    locks.append(name)
    _save_locks(locks)
    return locks


def unlock_snapshot(name: str) -> List[str]:
    """Unlock a previously locked snapshot."""
    locks = _load_locks()
    if name not in locks:
        raise SnapshotNotLockedError(f"Snapshot '{name}' is not locked.")

    locks.remove(name)
    _save_locks(locks)
    return locks


def is_locked(name: str) -> bool:
    """Return True if the snapshot is currently locked."""
    return name in _load_locks()


def get_locked_snapshots() -> List[str]:
    """Return all currently locked snapshot names."""
    return _load_locks()


def assert_not_locked(name: str) -> None:
    """Raise SnapshotAlreadyLockedError if the snapshot is locked."""
    if is_locked(name):
        raise SnapshotAlreadyLockedError(
            f"Snapshot '{name}' is locked and cannot be modified. "
            "Use 'stashpoint lock remove' to unlock it first."
        )
