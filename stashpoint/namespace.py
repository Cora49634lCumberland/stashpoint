"""Namespace support for grouping snapshots under a named prefix."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshots, save_snapshots


class SnapshotNotFoundError(Exception):
    pass


class NamespaceAlreadyExistsError(Exception):
    pass


class NamespaceNotFoundError(Exception):
    pass


def _get_namespaces_path() -> Path:
    return get_stash_path() / "namespaces.json"


def _load_namespaces() -> dict:
    path = _get_namespaces_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_namespaces(data: dict) -> None:
    path = _get_namespaces_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def create_namespace(name: str) -> dict:
    data = _load_namespaces()
    if name in data:
        raise NamespaceAlreadyExistsError(f"Namespace '{name}' already exists.")
    data[name] = []
    _save_namespaces(data)
    return data[name]


def delete_namespace(name: str) -> None:
    data = _load_namespaces()
    if name not in data:
        raise NamespaceNotFoundError(f"Namespace '{name}' not found.")
    del data[name]
    _save_namespaces(data)


def add_to_namespace(namespace: str, snapshot_name: str) -> list:
    snapshots = load_snapshots()
    if snapshot_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_namespaces()
    if namespace not in data:
        raise NamespaceNotFoundError(f"Namespace '{namespace}' not found.")
    if snapshot_name not in data[namespace]:
        data[namespace].append(snapshot_name)
    _save_namespaces(data)
    return data[namespace]


def remove_from_namespace(namespace: str, snapshot_name: str) -> list:
    data = _load_namespaces()
    if namespace not in data:
        raise NamespaceNotFoundError(f"Namespace '{namespace}' not found.")
    if snapshot_name in data[namespace]:
        data[namespace].remove(snapshot_name)
    _save_namespaces(data)
    return data[namespace]


def list_namespaces() -> dict:
    return _load_namespaces()


def get_namespace(name: str) -> list:
    data = _load_namespaces()
    if name not in data:
        raise NamespaceNotFoundError(f"Namespace '{name}' not found.")
    return data[name]
