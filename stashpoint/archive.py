"""Archive and unarchive snapshots (soft-delete with restore capability)."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshots, save_snapshots


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyArchivedError(Exception):
    pass


class SnapshotNotArchivedError(Exception):
    pass


def _get_archive_path() -> Path:
    return get_stash_path() / "archive.json"


def _load_archive() -> dict:
    path = _get_archive_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_archive(data: dict) -> None:
    path = _get_archive_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def archive_snapshot(name: str) -> dict:
    snapshots = load_snapshots()
    if name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    archive = _load_archive()
    if name in archive:
        raise SnapshotAlreadyArchivedError(f"Snapshot '{name}' is already archived.")
    archive[name] = snapshots.pop(name)
    save_snapshots(snapshots)
    _save_archive(archive)
    return archive[name]


def unarchive_snapshot(name: str) -> dict:
    archive = _load_archive()
    if name not in archive:
        raise SnapshotNotArchivedError(f"Snapshot '{name}' is not archived.")
    snapshots = load_snapshots()
    snapshots[name] = archive.pop(name)
    save_snapshots(snapshots)
    _save_archive(archive)
    return snapshots[name]


def list_archived() -> list[str]:
    return list(_load_archive().keys())


def purge_snapshot(name: str) -> None:
    archive = _load_archive()
    if name not in archive:
        raise SnapshotNotArchivedError(f"Snapshot '{name}' is not archived.")
    del archive[name]
    _save_archive(archive)
