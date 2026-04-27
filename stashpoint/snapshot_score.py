"""Snapshot scoring — assign and retrieve numeric scores for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when the target snapshot does not exist."""


class InvalidScoreError(Exception):
    """Raised when a score value is outside the accepted range."""


SCORE_MIN = 0
SCORE_MAX = 100


def _get_scores_path() -> Path:
    return get_stash_path() / "scores.json"


def _load_scores() -> Dict[str, int]:
    path = _get_scores_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_scores(scores: Dict[str, int]) -> None:
    path = _get_scores_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(scores, fh, indent=2)


def set_score(snapshot_name: str, score: int) -> int:
    """Assign *score* to *snapshot_name*. Returns the stored score."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    if not (SCORE_MIN <= score <= SCORE_MAX):
        raise InvalidScoreError(
            f"Score must be between {SCORE_MIN} and {SCORE_MAX}, got {score}."
        )
    scores = _load_scores()
    scores[snapshot_name] = score
    _save_scores(scores)
    return score


def get_score(snapshot_name: str) -> Optional[int]:
    """Return the score for *snapshot_name*, or ``None`` if not set."""
    return _load_scores().get(snapshot_name)


def remove_score(snapshot_name: str) -> None:
    """Remove the score entry for *snapshot_name* (no-op if absent)."""
    scores = _load_scores()
    scores.pop(snapshot_name, None)
    _save_scores(scores)


def list_scores(descending: bool = True) -> List[Tuple[str, int]]:
    """Return all scored snapshots sorted by score."""
    scores = _load_scores()
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=descending)
