"""Track and query how many times a snapshot has been restored or accessed."""

from __future__ import annotations

import json
from pathlib import Path

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


def _get_counts_path() -> Path:
    return get_stash_path() / "counts.json"


def _load_counts() -> dict[str, int]:
    path = _get_counts_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_counts(counts: dict[str, int]) -> None:
    path = _get_counts_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(counts, f, indent=2)


def increment_count(snapshot_name: str) -> int:
    """Increment the restore count for a snapshot. Returns the new count."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    counts = _load_counts()
    counts[snapshot_name] = counts.get(snapshot_name, 0) + 1
    _save_counts(counts)
    return counts[snapshot_name]


def get_count(snapshot_name: str) -> int:
    """Return the restore count for a snapshot (0 if never restored)."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    counts = _load_counts()
    return counts.get(snapshot_name, 0)


def reset_count(snapshot_name: str) -> None:
    """Reset the restore count for a snapshot to zero."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    counts = _load_counts()
    counts[snapshot_name] = 0
    _save_counts(counts)


def list_counts() -> list[dict]:
    """Return all snapshots with their counts, sorted by count descending."""
    counts = _load_counts()
    return sorted(
        [{"name": name, "count": count} for name, count in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
