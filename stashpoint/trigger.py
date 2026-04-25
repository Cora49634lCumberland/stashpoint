"""Trigger management for stashpoint snapshots.

Allows associating named triggers (e.g. 'on_git_branch_change', 'on_deploy')
with snapshots so tooling can query which snapshot to activate for a given event.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class TriggerAlreadyExistsError(Exception):
    pass


class TriggerNotFoundError(Exception):
    pass


def _get_triggers_path() -> Path:
    return get_stash_path() / "triggers.json"


def _load_triggers() -> Dict[str, str]:
    """Return mapping of trigger_name -> snapshot_name."""
    path = _get_triggers_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_triggers(triggers: Dict[str, str]) -> None:
    path = _get_triggers_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(triggers, indent=2))


def set_trigger(trigger_name: str, snapshot_name: str) -> str:
    """Associate *trigger_name* with *snapshot_name*.

    Raises SnapshotNotFoundError if the snapshot does not exist.
    Overwrites any existing mapping for this trigger.
    Returns the snapshot_name.
    """
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    triggers = _load_triggers()
    triggers[trigger_name] = snapshot_name
    _save_triggers(triggers)
    return snapshot_name


def remove_trigger(trigger_name: str) -> None:
    """Remove a trigger mapping.

    Raises TriggerNotFoundError if the trigger does not exist.
    """
    triggers = _load_triggers()
    if trigger_name not in triggers:
        raise TriggerNotFoundError(f"Trigger '{trigger_name}' not found.")
    del triggers[trigger_name]
    _save_triggers(triggers)


def resolve_trigger(trigger_name: str) -> Optional[str]:
    """Return the snapshot name bound to *trigger_name*, or None."""
    return _load_triggers().get(trigger_name)


def list_triggers() -> List[Dict[str, str]]:
    """Return all triggers as a list of dicts with 'trigger' and 'snapshot' keys."""
    triggers = _load_triggers()
    return [{"trigger": k, "snapshot": v} for k, v in sorted(triggers.items())]
