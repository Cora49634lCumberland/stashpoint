"""TTL (time-to-live) support for snapshots.

Allows setting a duration-based expiry on snapshots (e.g. '1h', '30m', '7d').
Builds on top of expire.py by converting human-readable durations to timestamps.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from stashpoint.storage import load_snapshots
from stashpoint.expire import set_expiry, get_expiry, remove_expiry, SnapshotNotFoundError

__all__ = [
    "InvalidTTLError",
    "SnapshotNotFoundError",
    "parse_ttl",
    "set_ttl",
    "get_ttl_remaining",
    "remove_ttl",
]

_UNIT_SECONDS: dict[str, int] = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}

_TTL_RE = re.compile(r"^(\d+)([smhdw])$", re.IGNORECASE)


class InvalidTTLError(ValueError):
    """Raised when a TTL string cannot be parsed."""


def parse_ttl(ttl: str) -> timedelta:
    """Parse a TTL string like '10m', '2h', '7d' into a timedelta.

    Args:
        ttl: Human-readable duration string.

    Returns:
        Corresponding timedelta.

    Raises:
        InvalidTTLError: If the format is not recognised.
    """
    match = _TTL_RE.match(ttl.strip())
    if not match:
        raise InvalidTTLError(
            f"Invalid TTL '{ttl}'. Use a number followed by s/m/h/d/w (e.g. '30m', '2h')."
        )
    amount = int(match.group(1))
    unit = match.group(2).lower()
    return timedelta(seconds=amount * _UNIT_SECONDS[unit])


def set_ttl(name: str, ttl: str) -> float:
    """Set a TTL on a snapshot, computing the absolute expiry timestamp.

    Args:
        name: Snapshot name.
        ttl: Duration string, e.g. '1h'.

    Returns:
        The computed expiry UNIX timestamp.

    Raises:
        InvalidTTLError: If the TTL string is invalid.
        SnapshotNotFoundError: If the snapshot does not exist.
    """
    delta = parse_ttl(ttl)
    expiry_dt = datetime.now(timezone.utc) + delta
    return set_expiry(name, expiry_dt.timestamp())


def get_ttl_remaining(name: str) -> timedelta | None:
    """Return the remaining TTL for a snapshot, or None if not set / already expired.

    Args:
        name: Snapshot name.

    Returns:
        Remaining timedelta, or None.
    """
    expiry_ts = get_expiry(name)
    if expiry_ts is None:
        return None
    remaining = expiry_ts - datetime.now(timezone.utc).timestamp()
    if remaining <= 0:
        return None
    return timedelta(seconds=remaining)


def remove_ttl(name: str) -> None:
    """Remove the TTL from a snapshot.

    Args:
        name: Snapshot name.
    """
    remove_expiry(name)
