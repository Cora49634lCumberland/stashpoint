"""Category management for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class CategoryAlreadyExistsError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


def _get_categories_path() -> Path:
    return get_stash_path() / "categories.json"


def _load_categories() -> Dict[str, List[str]]:
    path = _get_categories_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_categories(data: Dict[str, List[str]]) -> None:
    _get_categories_path().write_text(json.dumps(data, indent=2))


def create_category(name: str) -> str:
    """Create a new empty category."""
    data = _load_categories()
    if name in data:
        raise CategoryAlreadyExistsError(f"Category '{name}' already exists.")
    data[name] = []
    _save_categories(data)
    return name


def delete_category(name: str) -> None:
    """Delete a category (does not delete snapshots)."""
    data = _load_categories()
    if name not in data:
        raise CategoryNotFoundError(f"Category '{name}' not found.")
    del data[name]
    _save_categories(data)


def add_to_category(category: str, snapshot_name: str) -> List[str]:
    """Add a snapshot to a category."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_categories()
    if category not in data:
        raise CategoryNotFoundError(f"Category '{category}' not found.")
    if snapshot_name not in data[category]:
        data[category].append(snapshot_name)
        _save_categories(data)
    return data[category]


def remove_from_category(category: str, snapshot_name: str) -> List[str]:
    """Remove a snapshot from a category."""
    data = _load_categories()
    if category not in data:
        raise CategoryNotFoundError(f"Category '{category}' not found.")
    data[category] = [s for s in data[category] if s != snapshot_name]
    _save_categories(data)
    return data[category]


def get_category(name: str) -> List[str]:
    """Return all snapshot names in a category."""
    data = _load_categories()
    if name not in data:
        raise CategoryNotFoundError(f"Category '{name}' not found.")
    return data[name]


def list_categories() -> Dict[str, List[str]]:
    """Return all categories and their members."""
    return _load_categories()


def get_snapshot_categories(snapshot_name: str) -> List[str]:
    """Return all categories that contain the given snapshot."""
    data = _load_categories()
    return [cat for cat, members in data.items() if snapshot_name in members]
