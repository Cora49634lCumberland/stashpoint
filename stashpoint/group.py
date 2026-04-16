"""Group multiple snapshots under a named collection."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class GroupNotFoundError(Exception):
    pass


class GroupAlreadyExistsError(Exception):
    pass


def _get_groups_path() -> Path:
    return get_stash_path() / "groups.json"


def _load_groups() -> dict:
    path = _get_groups_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(groups: dict) -> None:
    path = _get_groups_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(groups, indent=2))


def create_group(name: str, snapshot_names: list[str]) -> dict:
    """Create a named group containing the given snapshots."""
    from stashpoint.storage import load_snapshots
    all_snapshots = load_snapshots()
    for sname in snapshot_names:
        if sname not in all_snapshots:
            raise SnapshotNotFoundError(f"Snapshot '{sname}' not found.")
    groups = _load_groups()
    if name in groups:
        raise GroupAlreadyExistsError(f"Group '{name}' already exists.")
    groups[name] = snapshot_names
    _save_groups(groups)
    return groups[name]


def delete_group(name: str) -> None:
    """Delete a group by name."""
    groups = _load_groups()
    if name not in groups:
        raise GroupNotFoundError(f"Group '{name}' not found.")
    del groups[name]
    _save_groups(groups)


def get_group(name: str) -> list[str]:
    """Return snapshot names in a group."""
    groups = _load_groups()
    if name not in groups:
        raise GroupNotFoundError(f"Group '{name}' not found.")
    return groups[name]


def list_groups() -> dict:
    """Return all groups."""
    return _load_groups()


def add_to_group(group_name: str, snapshot_name: str) -> list[str]:
    """Add a snapshot to an existing group."""
    from stashpoint.storage import load_snapshots
    all_snapshots = load_snapshots()
    if snapshot_name not in all_snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    groups = _load_groups()
    if group_name not in groups:
        raise GroupNotFoundError(f"Group '{group_name}' not found.")
    if snapshot_name not in groups[group_name]:
        groups[group_name].append(snapshot_name)
    _save_groups(groups)
    return groups[group_name]
