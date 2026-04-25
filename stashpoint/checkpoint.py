"""Checkpoint support: save a named point-in-time marker for a snapshot."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class CheckpointAlreadyExistsError(Exception):
    pass


class CheckpointNotFoundError(Exception):
    pass


def _get_checkpoints_path() -> Path:
    return get_stash_path() / "checkpoints.json"


def _load_checkpoints() -> dict:
    path = _get_checkpoints_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_checkpoints(data: dict) -> None:
    _get_checkpoints_path().write_text(json.dumps(data, indent=2))


def create_checkpoint(snapshot_name: str, checkpoint_name: str) -> dict:
    """Create a checkpoint entry for a snapshot at the current time."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")

    checkpoints = _load_checkpoints()
    key = f"{snapshot_name}::{checkpoint_name}"
    if key in checkpoints:
        raise CheckpointAlreadyExistsError(
            f"Checkpoint '{checkpoint_name}' already exists for '{snapshot_name}'."
        )

    entry = {
        "snapshot": snapshot_name,
        "checkpoint": checkpoint_name,
        "created_at": time.time(),
    }
    checkpoints[key] = entry
    _save_checkpoints(checkpoints)
    return entry


def remove_checkpoint(snapshot_name: str, checkpoint_name: str) -> None:
    """Remove a checkpoint."""
    checkpoints = _load_checkpoints()
    key = f"{snapshot_name}::{checkpoint_name}"
    if key not in checkpoints:
        raise CheckpointNotFoundError(
            f"Checkpoint '{checkpoint_name}' not found for '{snapshot_name}'."
        )
    del checkpoints[key]
    _save_checkpoints(checkpoints)


def get_checkpoints(snapshot_name: str) -> list[dict]:
    """Return all checkpoints for a snapshot, ordered by creation time."""
    checkpoints = _load_checkpoints()
    results = [
        v for k, v in checkpoints.items()
        if v["snapshot"] == snapshot_name
    ]
    return sorted(results, key=lambda e: e["created_at"])


def get_checkpoint(
    snapshot_name: str, checkpoint_name: str
) -> Optional[dict]:
    """Return a single checkpoint or None."""
    checkpoints = _load_checkpoints()
    return checkpoints.get(f"{snapshot_name}::{checkpoint_name}")
