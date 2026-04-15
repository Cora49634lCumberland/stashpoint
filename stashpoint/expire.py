"""Snapshot expiry: set a TTL on snapshots and query/purge expired ones."""

from __future__ import annotations

import time
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshots

_EXPIRY_FILE = "expiry.json"


class SnapshotNotFoundError(KeyError):
    pass


def _get_expiry_path():
    return get_stash_path() / _EXPIRY_FILE


def _load_expiry() -> dict:
    import json
    path = _get_expiry_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_expiry(data: dict) -> None:
    import json
    path = _get_expiry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_expiry(name: str, ttl_seconds: int) -> float:
    """Set a TTL (in seconds from now) on a snapshot. Returns the expiry timestamp."""
    snapshots = load_snapshots()
    if name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    expiry = _load_expiry()
    expires_at = time.time() + ttl_seconds
    expiry[name] = expires_at
    _save_expiry(expiry)
    return expires_at


def remove_expiry(name: str) -> None:
    """Remove the expiry from a snapshot."""
    expiry = _load_expiry()
    expiry.pop(name, None)
    _save_expiry(expiry)


def get_expiry(name: str) -> Optional[float]:
    """Return the expiry timestamp for a snapshot, or None if not set."""
    return _load_expiry().get(name)


def is_expired(name: str) -> bool:
    """Return True if the snapshot has passed its expiry time."""
    ts = get_expiry(name)
    if ts is None:
        return False
    return time.time() > ts


def list_expiring() -> list[dict]:
    """Return all snapshots that have an expiry set, with their status."""
    expiry = _load_expiry()
    now = time.time()
    result = []
    for name, ts in expiry.items():
        result.append({
            "name": name,
            "expires_at": ts,
            "expired": now > ts,
            "seconds_remaining": max(0.0, ts - now),
        })
    result.sort(key=lambda x: x["expires_at"])
    return result


def purge_expired() -> list[str]:
    """Delete all snapshots that have expired. Returns list of purged names."""
    from stashpoint.storage import load_snapshots, save_snapshots
    expiry = _load_expiry()
    now = time.time()
    purged = [name for name, ts in expiry.items() if now > ts]
    if not purged:
        return []
    snapshots = load_snapshots()
    for name in purged:
        snapshots.pop(name, None)
        expiry.pop(name, None)
    save_snapshots(snapshots)
    _save_expiry(expiry)
    return purged
