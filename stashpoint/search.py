"""Search snapshots by key or value patterns."""

from fnmatch import fnmatch
from stashpoint.storage import load_snapshots


class NoSnapshotsFoundError(Exception):
    pass


def search_by_key(pattern: str) -> dict[str, dict]:
    """Return snapshots that contain at least one key matching the glob pattern."""
    snapshots = load_snapshots()
    if not snapshots:
        raise NoSnapshotsFoundError("No snapshots stored.")

    results = {}
    for name, data in snapshots.items():
        matched = {k: v for k, v in data.items() if fnmatch(k, pattern)}
        if matched:
            results[name] = matched
    return results


def search_by_value(pattern: str) -> dict[str, dict]:
    """Return snapshots that contain at least one value matching the glob pattern."""
    snapshots = load_snapshots()
    if not snapshots:
        raise NoSnapshotsFoundError("No snapshots stored.")

    results = {}
    for name, data in snapshots.items():
        matched = {k: v for k, v in data.items() if fnmatch(str(v), pattern)}
        if matched:
            results[name] = matched
    return results


def search_snapshots(key_pattern: str | None = None, value_pattern: str | None = None) -> dict[str, dict]:
    """Search snapshots by key and/or value pattern. Both are optional glob patterns."""
    snapshots = load_snapshots()
    if not snapshots:
        raise NoSnapshotsFoundError("No snapshots stored.")

    results = {}
    for name, data in snapshots.items():
        matched = {}
        for k, v in data.items():
            key_ok = fnmatch(k, key_pattern) if key_pattern else True
            val_ok = fnmatch(str(v), value_pattern) if value_pattern else True
            if key_ok and val_ok:
                matched[k] = v
        if matched:
            results[name] = matched
    return results
