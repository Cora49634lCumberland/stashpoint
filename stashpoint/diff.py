"""Diff utilities for comparing environment variable snapshots."""

from typing import Optional
from stashpoint.storage import load_snapshot


def diff_snapshots(name_a: str, name_b: Optional[str] = None) -> dict:
    """
    Compare two named snapshots, or a snapshot against the current environment.

    Returns a dict with keys:
      - 'added':   vars in B but not in A
      - 'removed': vars in A but not in B
      - 'changed': vars present in both but with different values
      - 'unchanged': vars present in both with identical values
    """
    import os

    snapshot_a = load_snapshot(name_a)
    if snapshot_a is None:
        raise KeyError(f"Snapshot '{name_a}' not found.")

    if name_b is None:
        snapshot_b = dict(os.environ)
        label_b = "<current environment>"
    else:
        snapshot_b = load_snapshot(name_b)
        if snapshot_b is None:
            raise KeyError(f"Snapshot '{name_b}' not found.")
        label_b = name_b

    keys_a = set(snapshot_a.keys())
    keys_b = set(snapshot_b.keys())

    added = {k: snapshot_b[k] for k in keys_b - keys_a}
    removed = {k: snapshot_a[k] for k in keys_a - keys_b}
    changed = {
        k: {"before": snapshot_a[k], "after": snapshot_b[k]}
        for k in keys_a & keys_b
        if snapshot_a[k] != snapshot_b[k]
    }
    unchanged = {
        k: snapshot_a[k]
        for k in keys_a & keys_b
        if snapshot_a[k] == snapshot_b[k]
    }

    return {
        "label_a": name_a,
        "label_b": label_b,
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: dict) -> str:
    """Return a human-readable string representation of a diff result."""
    lines = [
        f"Comparing '{diff['label_a']}' → '{diff['label_b']}'",
        "",
    ]

    if diff["added"]:
        lines.append("  [+] Added:")
        for k, v in sorted(diff["added"].items()):
            lines.append(f"      {k}={v}")

    if diff["removed"]:
        lines.append("  [-] Removed:")
        for k, v in sorted(diff["removed"].items()):
            lines.append(f"      {k}={v}")

    if diff["changed"]:
        lines.append("  [~] Changed:")
        for k, vals in sorted(diff["changed"].items()):
            lines.append(f"      {k}: '{vals['before']}' → '{vals['after']}'")

    if not diff["added"] and not diff["removed"] and not diff["changed"]:
        lines.append("  No differences found.")

    return "\n".join(lines)
