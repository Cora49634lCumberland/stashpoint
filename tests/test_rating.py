"""Tests for stashpoint.rating."""

from __future__ import annotations

import pytest

from stashpoint.rating import (
    InvalidRatingError,
    SnapshotNotFoundError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.STASH_DIR", tmp_path)
    monkeypatch.setattr("stashpoint.rating._get_ratings_path",
                        lambda: tmp_path / "ratings.json")
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_set_rating_returns_rating(isolated_stash):
    _save("snap1")
    result = set_rating("snap1", 4)
    assert result == 4


def test_get_rating_returns_stored(isolated_stash):
    _save("snap1")
    set_rating("snap1", 3)
    assert get_rating("snap1") == 3


def test_get_rating_returns_none_when_not_set(isolated_stash):
    _save("snap1")
    assert get_rating("snap1") is None


def test_set_rating_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_rating("ghost", 5)


def test_set_rating_invalid_low_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(InvalidRatingError):
        set_rating("snap1", 0)


def test_set_rating_invalid_high_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(InvalidRatingError):
        set_rating("snap1", 6)


def test_set_rating_overwrites_existing(isolated_stash):
    _save("snap1")
    set_rating("snap1", 2)
    set_rating("snap1", 5)
    assert get_rating("snap1") == 5


def test_remove_rating_clears_entry(isolated_stash):
    _save("snap1")
    set_rating("snap1", 4)
    remove_rating("snap1")
    assert get_rating("snap1") is None


def test_remove_rating_noop_when_not_set(isolated_stash):
    _save("snap1")
    remove_rating("snap1")  # should not raise


def test_list_ratings_returns_all(isolated_stash):
    _save("a")
    _save("b")
    set_rating("a", 1)
    set_rating("b", 5)
    result = list_ratings()
    assert result == {"a": 1, "b": 5}


def test_list_ratings_empty_when_none_set(isolated_stash):
    assert list_ratings() == {}
