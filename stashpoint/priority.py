"""Priority management for snapshots."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshot

VALID_PRIORITIES = ("low", "normal", "high", "critical")


class SnapshotNotFoundError(Exception):
    pass


class InvalidPriorityError(Exception):
    pass


def _get_priority_path() -> Path:
    return get_stash_path() / "priorities.json"


def _load_priorities() -> dict:
    path = _get_priority_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_priorities(data: dict) -> None:
    path = _get_priority_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_priority(name: str, priority: str) -> str:
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
    if priority not in VALID_PRIORITIES:
        raise InvalidPriorityError(
            f"Invalid priority '{priority}'. Choose from: {', '.join(VALID_PRIORITIES)}"
        )
    data = _load_priorities()
    data[name] = priority
    _save_priorities(data)
    return priority


def get_priority(name: str) -> str | None:
    data = _load_priorities()
    return data.get(name)


def remove_priority(name: str) -> None:
    data = _load_priorities()
    if name not in data:
        return
    del data[name]
    _save_priorities(data)


def list_by_priority(priority: str) -> list[str]:
    if priority not in VALID_PRIORITIES:
        raise InvalidPriorityError(
            f"Invalid priority '{priority}'. Choose from: {', '.join(VALID_PRIORITIES)}"
        )
    data = _load_priorities()
    return [name for name, p in data.items() if p == priority]
