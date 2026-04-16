"""Watch a snapshot for environment variable drift."""

import os
from typing import Optional
from stashpoint.storage import load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class DriftResult:
    def __init__(self, snapshot_name: str, added: dict, removed: dict, changed: dict):
        self.snapshot_name = snapshot_name
        self.added = added
        self.removed = removed
        self.changed = changed

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def check_drift(snapshot_name: str, keys: Optional[list[str]] = None) -> DriftResult:
    """Compare a saved snapshot against the current environment."""
    data = load_snapshot(snapshot_name)
    if data is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")

    if keys:
        data = {k: v for k, v in data.items() if k in keys}

    current = {k: os.environ.get(k) for k in data}

    added = {k: os.environ[k] for k in os.environ if k not in data and (not keys or k in keys)}
    removed = {k: v for k, v in data.items() if k not in os.environ}
    changed = {
        k: {"snapshot": v, "current": os.environ[k]}
        for k, v in data.items()
        if k in os.environ and os.environ[k] != v
    }

    return DriftResult(snapshot_name, added, removed, changed)


def format_drift(result: DriftResult) -> str:
    if not result.has_drift:
        return f"No drift detected for snapshot '{result.snapshot_name}'."

    lines = [f"Drift detected for snapshot '{result.snapshot_name}':\n"]
    for k, v in result.added.items():
        lines.append(f"  + {k}={v}  (added in env)")
    for k, v in result.removed.items():
        lines.append(f"  - {k}={v}  (removed from env)")
    for k, vals in result.changed.items():
        lines.append(f"  ~ {k}: '{vals['snapshot']}' -> '{vals['current']}'")
    return "\n".join(lines)
