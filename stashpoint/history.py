"""Track snapshot creation and restoration history."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from stashpoint.storage import get_stash_path

HISTORY_FILE = "history.json"
MAX_HISTORY_ENTRIES = 100


def _get_history_path() -> str:
    return os.path.join(get_stash_path(), HISTORY_FILE)


def _load_history() -> list:
    path = _get_history_path()
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_history(entries: list) -> None:
    path = _get_history_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries[-MAX_HISTORY_ENTRIES:], f, indent=2)


def record_event(action: str, snapshot_name: str, meta: Optional[dict] = None) -> None:
    """Record a history event for a snapshot action.

    Args:
        action: One of 'save', 'restore', 'drop', 'export', 'import', 'merge'.
        snapshot_name: The name of the snapshot involved.
        meta: Optional extra metadata to store with the event.
    """
    entries = _load_history()
    entry = {
        "action": action,
        "snapshot": snapshot_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if meta:
        entry["meta"] = meta
    entries.append(entry)
    _save_history(entries)


def get_history(snapshot_name: Optional[str] = None, limit: Optional[int] = None) -> list:
    """Return history entries, optionally filtered by snapshot name.

    Args:
        snapshot_name: If provided, only return entries for this snapshot.
        limit: Maximum number of entries to return (most recent first).

    Returns:
        List of history entry dicts.
    """
    entries = _load_history()
    if snapshot_name:
        entries = [e for e in entries if e["snapshot"] == snapshot_name]
    entries = list(reversed(entries))
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_history(snapshot_name: Optional[str] = None) -> int:
    """Clear history entries.

    Args:
        snapshot_name: If provided, only clear entries for this snapshot.

    Returns:
        Number of entries removed.
    """
    entries = _load_history()
    if snapshot_name:
        remaining = [e for e in entries if e["snapshot"] != snapshot_name]
    else:
        remaining = []
    removed = len(entries) - len(remaining)
    _save_history(remaining)
    return removed
