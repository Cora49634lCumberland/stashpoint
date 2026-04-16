"""Validate snapshot contents against a schema of required/forbidden keys."""

from __future__ import annotations
from dataclasses import dataclass, field
from stashpoint.storage import load_snapshot


class SnapshotNotFoundError(Exception):
    pass


@dataclass
class ValidationResult:
    snapshot_name: str
    missing_keys: list[str] = field(default_factory=list)
    forbidden_keys: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.missing_keys and not self.forbidden_keys

    def summary(self) -> str:
        lines = [f"Snapshot: {self.snapshot_name}"]
        if self.is_valid:
            lines.append("  ✓ All checks passed.")
        else:
            for k in self.missing_keys:
                lines.append(f"  ✗ Missing required key: {k}")
            for k in self.forbidden_keys:
                lines.append(f"  ✗ Forbidden key present: {k}")
        return "\n".join(lines)


def validate_snapshot(
    name: str,
    required: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> ValidationResult:
    data = load_snapshot(name)
    if data is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' not found.")

    required = required or []
    forbidden = forbidden or []

    missing = [k for k in required if k not in data]
    present_forbidden = [k for k in forbidden if k in data]

    return ValidationResult(
        snapshot_name=name,
        missing_keys=missing,
        forbidden_keys=present_forbidden,
    )
