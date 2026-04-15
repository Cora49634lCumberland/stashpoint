"""Merge two or more snapshots into a single named snapshot."""

from typing import Optional
from stashpoint.storage import load_snapshot, save_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when a referenced snapshot does not exist."""


def merge_snapshots(
    source_names: list[str],
    target_name: str,
    overwrite: bool = False,
    strategy: str = "last-wins",
) -> dict[str, str]:
    """Merge multiple snapshots into a new snapshot.

    Args:
        source_names: Ordered list of snapshot names to merge.
        target_name: Name to save the merged snapshot under.
        overwrite: If False and target_name already exists, raise ValueError.
        strategy: Merge strategy. 'last-wins' (default) means later sources
                  override earlier ones for conflicting keys.

    Returns:
        The merged snapshot dict.

    Raises:
        SnapshotNotFoundError: If any source snapshot does not exist.
        ValueError: If target already exists and overwrite is False.
    """
    if not source_names:
        raise ValueError("At least one source snapshot name must be provided.")

    if strategy not in ("last-wins", "first-wins"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    existing_target = load_snapshot(target_name)
    if existing_target is not None and not overwrite:
        raise ValueError(
            f"Snapshot '{target_name}' already exists. Use overwrite=True to replace it."
        )

    merged: dict[str, str] = {}
    sources: list[dict[str, str]] = []

    for name in source_names:
        snapshot = load_snapshot(name)
        if snapshot is None:
            raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
        sources.append(snapshot)

    if strategy == "last-wins":
        for snapshot in sources:
            merged.update(snapshot)
    else:  # first-wins
        for snapshot in reversed(sources):
            merged.update(snapshot)

    save_snapshot(target_name, merged)
    return merged


def get_merge_conflicts(source_names: list[str]) -> dict[str, list[str]]:
    """Return keys that differ across the given snapshots.

    Returns:
        A dict mapping conflicting key -> list of distinct values across sources.
    """
    snapshots: list[tuple[str, dict[str, str]]] = []
    for name in source_names:
        snapshot = load_snapshot(name)
        if snapshot is None:
            raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
        snapshots.append((name, snapshot))

    all_keys: set[str] = set()
    for _, snap in snapshots:
        all_keys.update(snap.keys())

    conflicts: dict[str, list[str]] = {}
    for key in all_keys:
        values = list({snap.get(key) for _, snap in snapshots if key in snap})
        if len(values) > 1:
            conflicts[key] = values

    return conflicts
