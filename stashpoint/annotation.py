"""Inline key-value annotations attached to a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class AnnotationKeyNotFoundError(Exception):
    pass


def _get_annotations_path() -> Path:
    return get_stash_path() / "annotations.json"


def _load_annotations() -> Dict[str, Dict[str, str]]:
    path = _get_annotations_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_annotations(data: Dict[str, Dict[str, str]]) -> None:
    _get_annotations_path().write_text(json.dumps(data, indent=2))


def set_annotation(snapshot_name: str, key: str, value: str) -> Dict[str, str]:
    """Set a single annotation key on a snapshot."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_annotations()
    annotations = data.setdefault(snapshot_name, {})
    annotations[key] = value
    _save_annotations(data)
    return dict(annotations)


def get_annotation(snapshot_name: str, key: str) -> Optional[str]:
    """Return the value of a single annotation key, or None if absent."""
    data = _load_annotations()
    return data.get(snapshot_name, {}).get(key)


def remove_annotation(snapshot_name: str, key: str) -> Dict[str, str]:
    """Remove an annotation key from a snapshot."""
    data = _load_annotations()
    annotations = data.get(snapshot_name, {})
    if key not in annotations:
        raise AnnotationKeyNotFoundError(
            f"Annotation key '{key}' not found on snapshot '{snapshot_name}'."
        )
    del annotations[key]
    data[snapshot_name] = annotations
    _save_annotations(data)
    return dict(annotations)


def get_all_annotations(snapshot_name: str) -> Dict[str, str]:
    """Return all annotations for a snapshot."""
    return dict(_load_annotations().get(snapshot_name, {}))


def list_annotated_snapshots() -> Dict[str, Dict[str, str]]:
    """Return all snapshots that have at least one annotation."""
    return {k: dict(v) for k, v in _load_annotations().items() if v}
