"""Compare multiple snapshots side-by-side, highlighting shared and unique keys."""

from typing import Optional
from stashpoint.storage import load_snapshot


class SnapshotNotFoundError(Exception):
    pass


def compare_snapshots(names: list[str]) -> dict:
    """Load multiple snapshots and return a comparison structure.

    Returns a dict with:
      - 'keys': sorted list of all keys across all snapshots
      - 'snapshots': dict of name -> {key -> value or None}
      - 'shared': keys present in ALL snapshots
      - 'unique': dict of name -> keys only in that snapshot
    """
    if len(names) < 2:
        raise ValueError("At least two snapshot names are required for comparison.")

    loaded: dict[str, dict[str, str]] = {}
    for name in names:
        snap = load_snapshot(name)
        if snap is None:
            raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")
        loaded[name] = snap

    all_keys: set[str] = set()
    for snap in loaded.values():
        all_keys.update(snap.keys())

    sorted_keys = sorted(all_keys)

    matrix: dict[str, dict[str, Optional[str]]] = {}
    for name, snap in loaded.items():
        matrix[name] = {key: snap.get(key) for key in sorted_keys}

    shared = [
        key for key in sorted_keys
        if all(key in loaded[name] for name in names)
    ]

    unique: dict[str, list[str]] = {}
    for name in names:
        unique[name] = [
            key for key in sorted_keys
            if key in loaded[name] and all(
                key not in loaded[other] for other in names if other != name
            )
        ]

    return {
        "keys": sorted_keys,
        "snapshots": matrix,
        "shared": shared,
        "unique": unique,
    }


def format_compare(result: dict) -> str:
    """Render a comparison result as a human-readable table string."""
    names = list(result["snapshots"].keys())
    keys = result["keys"]

    col_width = max((len(n) for n in names), default=10)
    key_width = max((len(k) for k in keys), default=10)

    header = f"{'KEY':<{key_width}}  " + "  ".join(f"{n:<{col_width}}" for n in names)
    separator = "-" * len(header)
    lines = [header, separator]

    for key in keys:
        row = f"{key:<{key_width}}  "
        values = []
        for name in names:
            val = result["snapshots"][name][key]
            values.append(f"{(val if val is not None else '<missing>'):<{col_width}}")
        row += "  ".join(values)
        lines.append(row)

    lines.append(separator)
    lines.append(f"Shared keys ({len(result['shared'])}): {', '.join(result['shared']) or 'none'}")
    for name in names:
        u = result["unique"][name]
        lines.append(f"Unique to '{name}' ({len(u)}): {', '.join(u) or 'none'}")

    return "\n".join(lines)
