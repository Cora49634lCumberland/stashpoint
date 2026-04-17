"""Assign and manage human-friendly labels for snapshots."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class LabelAlreadyExistsError(Exception):
    pass


class LabelNotFoundError(Exception):
    pass


def _get_labels_path() -> Path:
    return get_stash_path() / "labels.json"


def _load_labels() -> dict:
    path = _get_labels_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_labels(labels: dict) -> None:
    _get_labels_path().write_text(json.dumps(labels, indent=2))


def set_label(snapshot_name: str, label: str) -> str:
    """Assign a label to a snapshot. Raises if snapshot does not exist."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    labels = _load_labels()
    labels[label] = snapshot_name
    _save_labels(labels)
    return label


def remove_label(label: str) -> None:
    """Remove a label. Raises if label does not exist."""
    labels = _load_labels()
    if label not in labels:
        raise LabelNotFoundError(f"Label '{label}' not found.")
    del labels[label]
    _save_labels(labels)


def resolve_label(label: str) -> str:
    """Return the snapshot name for a label. Raises if not found."""
    labels = _load_labels()
    if label not in labels:
        raise LabelNotFoundError(f"Label '{label}' not found.")
    return labels[label]


def list_labels() -> dict:
    """Return all label -> snapshot_name mappings."""
    return _load_labels()
