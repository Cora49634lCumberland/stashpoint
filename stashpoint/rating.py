"""Snapshot rating module — assign a 1-5 star rating to named snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when the target snapshot does not exist."""


class InvalidRatingError(Exception):
    """Raised when the provided rating is outside the 1-5 range."""


VALID_RATINGS = frozenset(range(1, 6))


def _get_ratings_path() -> Path:
    return get_stash_path() / "ratings.json"


def _load_ratings() -> dict[str, int]:
    path = _get_ratings_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_ratings(ratings: dict[str, int]) -> None:
    _get_ratings_path().write_text(json.dumps(ratings, indent=2))


def set_rating(snapshot_name: str, rating: int) -> int:
    """Set the rating for *snapshot_name*. Returns the stored rating."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' does not exist.")
    if rating not in VALID_RATINGS:
        raise InvalidRatingError(f"Rating must be between 1 and 5, got {rating}.")
    ratings = _load_ratings()
    ratings[snapshot_name] = rating
    _save_ratings(ratings)
    return rating


def get_rating(snapshot_name: str) -> Optional[int]:
    """Return the rating for *snapshot_name*, or None if not rated."""
    return _load_ratings().get(snapshot_name)


def remove_rating(snapshot_name: str) -> None:
    """Remove the rating for *snapshot_name* if one exists."""
    ratings = _load_ratings()
    ratings.pop(snapshot_name, None)
    _save_ratings(ratings)


def list_ratings() -> dict[str, int]:
    """Return all snapshot ratings as a dict of {name: rating}."""
    return _load_ratings()
