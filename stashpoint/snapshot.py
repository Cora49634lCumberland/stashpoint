"""Core logic for capturing and restoring environment variable snapshots."""

import os
from typing import Dict, List, Optional

from stashpoint.storage import (
    delete_snapshot,
    list_snapshot_names,
    load_snapshot,
    save_snapshot,
)


def capture(name: str, keys: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Capture current environment variables as a named snapshot.

    Args:
        name: The snapshot name.
        keys: Optional list of specific keys to capture. Captures all if None.

    Returns:
        The captured environment variables dict.
    """
    if keys:
        env_vars = {k: os.environ[k] for k in keys if k in os.environ}
    else:
        env_vars = dict(os.environ)

    save_snapshot(name, env_vars)
    return env_vars


def restore(name: str, overwrite: bool = True) -> Dict[str, str]:
    """
    Restore a named snapshot into the current process environment.

    Args:
        name: The snapshot name to restore.
        overwrite: If True, overwrite existing env vars with snapshot values.

    Returns:
        The restored environment variables dict.

    Raises:
        KeyError: If the snapshot does not exist.
    """
    env_vars = load_snapshot(name)
    if env_vars is None:
        raise KeyError(f"Snapshot '{name}' not found.")

    for key, value in env_vars.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value

    return env_vars


def drop(name: str) -> bool:
    """Delete a snapshot by name."""
    return delete_snapshot(name)


def list_snapshots() -> List[str]:
    """Return all stored snapshot names."""
    return list_snapshot_names()


def show(name: str) -> Dict[str, str]:
    """Return the contents of a named snapshot without applying it."""
    env_vars = load_snapshot(name)
    if env_vars is None:
        raise KeyError(f"Snapshot '{name}' not found.")
    return env_vars


def diff(name: str) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Compare a named snapshot against the current environment.

    Returns a dict of keys that differ, where each value is a dict with
    'snapshot' and 'current' entries showing the respective values.
    Keys present in only one side will have None for the missing side.

    Args:
        name: The snapshot name to compare.

    Returns:
        A dict of differing keys to their snapshot vs current values.

    Raises:
        KeyError: If the snapshot does not exist.
    """
    snapshot_vars = load_snapshot(name)
    if snapshot_vars is None:
        raise KeyError(f"Snapshot '{name}' not found.")

    current_vars = dict(os.environ)
    all_keys = set(snapshot_vars) | set(current_vars)

    return {
        key: {"snapshot": snapshot_vars.get(key), "current": current_vars.get(key)}
        for key in all_keys
        if snapshot_vars.get(key) != current_vars.get(key)
    }
