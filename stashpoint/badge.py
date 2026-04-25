"""Badge system for snapshots — assign visual badges (e.g. 'stable', 'wip', 'prod') to snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when the target snapshot does not exist."""


class BadgeAlreadyExistsError(Exception):
    """Raised when a badge has already been assigned to a snapshot."""


class BadgeNotFoundError(Exception):
    """Raised when a badge is not assigned to a snapshot."""


VALID_BADGES = {"stable", "wip", "prod", "dev", "deprecated", "experimental", "archived"}


def _get_badges_path() -> Path:
    return get_stash_path() / "badges.json"


def _load_badges() -> dict:
    path = _get_badges_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_badges(data: dict) -> None:
    path = _get_badges_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def add_badge(snapshot_name: str, badge: str) -> List[str]:
    """Assign a badge to a snapshot. Returns the updated badge list."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_badges()
    badges: List[str] = data.get(snapshot_name, [])
    if badge in badges:
        raise BadgeAlreadyExistsError(f"Badge '{badge}' already assigned to '{snapshot_name}'.")
    badges.append(badge)
    data[snapshot_name] = badges
    _save_badges(data)
    return badges


def remove_badge(snapshot_name: str, badge: str) -> List[str]:
    """Remove a badge from a snapshot. Returns the updated badge list."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_badges()
    badges: List[str] = data.get(snapshot_name, [])
    if badge not in badges:
        raise BadgeNotFoundError(f"Badge '{badge}' is not assigned to '{snapshot_name}'.")
    badges.remove(badge)
    data[snapshot_name] = badges
    _save_badges(data)
    return badges


def get_badges(snapshot_name: str) -> List[str]:
    """Return all badges assigned to a snapshot."""
    data = _load_badges()
    return data.get(snapshot_name, [])


def find_by_badge(badge: str) -> List[str]:
    """Return all snapshot names that carry the given badge."""
    data = _load_badges()
    return [name for name, badges in data.items() if badge in badges]
