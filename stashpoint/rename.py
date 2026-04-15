"""Rename a snapshot, updating all associated metadata."""

from stashpoint.storage import load_snapshots, save_snapshots, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyExistsError(Exception):
    pass


def rename_snapshot(old_name: str, new_name: str, stash_path=None) -> None:
    """Rename a snapshot from old_name to new_name.

    Raises SnapshotNotFoundError if old_name does not exist.
    Raises SnapshotAlreadyExistsError if new_name already exists.
    Raises ValueError if old_name and new_name are the same.
    """
    if old_name == new_name:
        raise ValueError("New name must be different from the current name.")

    snapshots = load_snapshots(stash_path)

    if old_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{old_name}' not found.")

    if new_name in snapshots:
        raise SnapshotAlreadyExistsError(
            f"Snapshot '{new_name}' already exists. Drop it first or choose a different name."
        )

    snapshots[new_name] = snapshots.pop(old_name)
    save_snapshots(snapshots, stash_path)

    # Propagate rename to tags, pins, and locks if those files exist
    _rename_in_json_set_file("tags.json", old_name, new_name, stash_path)
    _rename_in_json_set_file("pins.json", old_name, new_name, stash_path)
    _rename_in_json_set_file("locks.json", old_name, new_name, stash_path)


def _rename_in_json_set_file(
    filename: str, old_name: str, new_name: str, stash_path=None
) -> None:
    """Update a JSON file that maps snapshot names to lists/sets of values."""
    import json
    from stashpoint.storage import get_stash_path
    from pathlib import Path

    base = Path(stash_path) if stash_path else get_stash_path()
    filepath = base / filename

    if not filepath.exists():
        return

    with open(filepath, "r") as f:
        data = json.load(f)

    if old_name in data:
        data[new_name] = data.pop(old_name)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
