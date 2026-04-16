"""Audit log: record and retrieve mutation events for snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path

_AUDIT_FILE = "audit.json"


def _get_audit_path() -> Path:
    return get_stash_path() / _AUDIT_FILE


def _load_audit() -> list[dict]:
    path = _get_audit_path()
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def _save_audit(entries: list[dict]) -> None:
    path = _get_audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(entries, f, indent=2)


def record_action(
    action: str,
    snapshot_name: str,
    detail: Optional[str] = None,
) -> dict:
    """Append an audit entry and return it."""
    entries = _load_audit()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot_name,
        "detail": detail,
    }
    entries.append(entry)
    _save_audit(entries)
    return entry


def get_audit_log(
    snapshot_name: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """Return audit entries, newest first, with optional filters."""
    entries = _load_audit()
    if snapshot_name:
        entries = [e for e in entries if e["snapshot"] == snapshot_name]
    if action:
        entries = [e for e in entries if e["action"] == action]
    return list(reversed(entries))[:limit]


def clear_audit_log() -> int:
    """Delete all audit entries. Returns count removed."""
    entries = _load_audit()
    count = len(entries)
    _save_audit([])
    return count
