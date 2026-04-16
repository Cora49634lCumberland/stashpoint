"""Schedule automatic snapshot captures at named intervals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path
from stashpoint.snapshot import capture


class SnapshotNotFoundError(Exception):
    pass


class ScheduleAlreadyExistsError(Exception):
    pass


class ScheduleNotFoundError(Exception):
    pass


VALID_INTERVALS = ("hourly", "daily", "weekly")


def _get_schedule_path() -> Path:
    return get_stash_path() / "schedules.json"


def _load_schedules() -> dict:
    p = _get_schedule_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schedules(data: dict) -> None:
    p = _get_schedule_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_schedule(snapshot_name: str, interval: str, snapshots: Optional[dict] = None) -> dict:
    """Register a schedule for a snapshot. snapshots dict used for existence check."""
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval '{interval}'. Choose from {VALID_INTERVALS}.")
    if snapshots is not None and snapshot_name not in snapshots:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    data = _load_schedules()
    data[snapshot_name] = {"interval": interval}
    _save_schedules(data)
    return data[snapshot_name]


def remove_schedule(snapshot_name: str) -> None:
    data = _load_schedules()
    if snapshot_name not in data:
        raise ScheduleNotFoundError(f"No schedule for '{snapshot_name}'.")
    del data[snapshot_name]
    _save_schedules(data)


def get_schedule(snapshot_name: str) -> Optional[dict]:
    return _load_schedules().get(snapshot_name)


def list_schedules() -> dict:
    return _load_schedules()
