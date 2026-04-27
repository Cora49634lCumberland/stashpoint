"""Tests for stashpoint.snapshot_score."""

from __future__ import annotations

import pytest

from stashpoint.snapshot_score import (
    InvalidScoreError,
    SnapshotNotFoundError,
    get_score,
    list_scores,
    remove_score,
    set_score,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "val"})


# ---------------------------------------------------------------------------
# set_score
# ---------------------------------------------------------------------------

def test_set_score_returns_score():
    _save("snap")
    assert set_score("snap", 75) == 75


def test_set_score_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_score("ghost", 50)


def test_set_score_below_min_raises():
    _save("snap")
    with pytest.raises(InvalidScoreError):
        set_score("snap", -1)


def test_set_score_above_max_raises():
    _save("snap")
    with pytest.raises(InvalidScoreError):
        set_score("snap", 101)


def test_set_score_boundary_values():
    _save("low")
    _save("high")
    assert set_score("low", 0) == 0
    assert set_score("high", 100) == 100


# ---------------------------------------------------------------------------
# get_score
# ---------------------------------------------------------------------------

def test_get_score_returns_stored():
    _save("snap")
    set_score("snap", 42)
    assert get_score("snap") == 42


def test_get_score_returns_none_when_not_set():
    _save("snap")
    assert get_score("snap") is None


# ---------------------------------------------------------------------------
# remove_score
# ---------------------------------------------------------------------------

def test_remove_score_clears_entry():
    _save("snap")
    set_score("snap", 55)
    remove_score("snap")
    assert get_score("snap") is None


def test_remove_score_noop_when_absent():
    _save("snap")
    remove_score("snap")  # should not raise


# ---------------------------------------------------------------------------
# list_scores
# ---------------------------------------------------------------------------

def test_list_scores_sorted_descending():
    for name, score in [("a", 10), ("b", 90), ("c", 50)]:
        _save(name)
        set_score(name, score)
    result = list_scores(descending=True)
    scores_only = [s for _, s in result]
    assert scores_only == sorted(scores_only, reverse=True)


def test_list_scores_sorted_ascending():
    for name, score in [("x", 30), ("y", 80)]:
        _save(name)
        set_score(name, score)
    result = list_scores(descending=False)
    scores_only = [s for _, s in result]
    assert scores_only == sorted(scores_only)


def test_list_scores_empty_when_none_set():
    assert list_scores() == []
