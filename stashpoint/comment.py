"""Inline comment support for snapshots.

Allows attaching a short comment (distinct from a full description or note)
to a snapshot — useful for quick annotations like 'pre-deploy' or 'WIP'.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when the target snapshot does not exist."""


def _get_comments_path() -> Path:
    return get_stash_path() / "comments.json"


def _load_comments() -> dict[str, str]:
    path = _get_comments_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_comments(data: dict[str, str]) -> None:
    path = _get_comments_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_comment(snapshot_name: str, comment: str) -> str:
    """Attach *comment* to *snapshot_name*. Returns the stored comment."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    data = _load_comments()
    data[snapshot_name] = comment
    _save_comments(data)
    return comment


def get_comment(snapshot_name: str) -> Optional[str]:
    """Return the comment for *snapshot_name*, or None if unset."""
    return _load_comments().get(snapshot_name)


def remove_comment(snapshot_name: str) -> None:
    """Remove the comment for *snapshot_name* (no-op if not set)."""
    data = _load_comments()
    data.pop(snapshot_name, None)
    _save_comments(data)


def list_comments() -> dict[str, str]:
    """Return all snapshot-name → comment mappings."""
    return _load_comments()
