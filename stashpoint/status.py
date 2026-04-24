"""Snapshot status tracking: active, draft, or deprecated."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import get_stash_path, load_snapshot

VALID_STATUSES = {"active", "draft", "deprecated"}


class SnapshotNotFoundError(Exception):
    pass


class InvalidStatusError(Exception):
    pass


def _get_status_path() -> Path:
    return get_stash_path() / "statuses.json"


def _load_statuses() -> Dict[str, str]:
    path = _get_status_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_statuses(statuses: Dict[str, str]) -> None:
    _get_status_path().write_text(json.dumps(statuses, indent=2))


def set_status(name: str, status: str) -> str:
    """Set the status for a snapshot. Returns the new status."""
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' does not exist.")
    if status not in VALID_STATUSES:
        raise InvalidStatusError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}."
        )
    statuses = _load_statuses()
    statuses[name] = status
    _save_statuses(statuses)
    return status


def get_status(name: str) -> Optional[str]:
    """Return the status of a snapshot, or None if not set."""
    return _load_statuses().get(name)


def remove_status(name: str) -> None:
    """Remove the status entry for a snapshot."""
    statuses = _load_statuses()
    statuses.pop(name, None)
    _save_statuses(statuses)


def list_by_status(status: str) -> List[str]:
    """Return all snapshot names with the given status."""
    if status not in VALID_STATUSES:
        raise InvalidStatusError(
            f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}."
        )
    statuses = _load_statuses()
    return [name for name, s in statuses.items() if s == status]
