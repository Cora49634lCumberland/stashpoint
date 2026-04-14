"""Handles persistent storage of environment variable snapshots."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STASH_DIR = Path.home() / ".stashpoint"
STASH_FILE = "snapshots.json"


def get_stash_path() -> Path:
    """Return the path to the stash directory, creating it if needed."""
    stash_dir = Path(os.environ.get("STASHPOINT_DIR", DEFAULT_STASH_DIR))
    stash_dir.mkdir(parents=True, exist_ok=True)
    return stash_dir


def load_snapshots() -> Dict[str, Dict[str, str]]:
    """Load all snapshots from disk. Returns empty dict if none exist."""
    stash_file = get_stash_path() / STASH_FILE
    if not stash_file.exists():
        return {}
    with open(stash_file, "r") as f:
        return json.load(f)


def save_snapshots(snapshots: Dict[str, Dict[str, str]]) -> None:
    """Persist all snapshots to disk."""
    stash_file = get_stash_path() / STASH_FILE
    with open(stash_file, "w") as f:
        json.dump(snapshots, f, indent=2)


def save_snapshot(name: str, env_vars: Dict[str, str]) -> None:
    """Save a named snapshot, overwriting if it already exists."""
    snapshots = load_snapshots()
    snapshots[name] = env_vars
    save_snapshots(snapshots)


def load_snapshot(name: str) -> Optional[Dict[str, str]]:
    """Load a single snapshot by name. Returns None if not found."""
    return load_snapshots().get(name)


def delete_snapshot(name: str) -> bool:
    """Delete a snapshot by name. Returns True if deleted, False if not found."""
    snapshots = load_snapshots()
    if name not in snapshots:
        return False
    del snapshots[name]
    save_snapshots(snapshots)
    return True


def list_snapshot_names() -> list:
    """Return a sorted list of all snapshot names."""
    return sorted(load_snapshots().keys())
