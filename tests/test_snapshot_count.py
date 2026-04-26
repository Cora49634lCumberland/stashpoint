"""Tests for stashpoint.snapshot_count."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.snapshot_count import (
    SnapshotNotFoundError,
    get_count,
    increment_count,
    list_counts,
    reset_count,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    storage.save_snapshot(name, data or {"KEY": "value"})


def test_get_count_returns_zero_when_never_incremented():
    _save("snap")
    assert get_count("snap") == 0


def test_increment_count_returns_new_count():
    _save("snap")
    result = increment_count("snap")
    assert result == 1


def test_increment_count_accumulates():
    _save("snap")
    increment_count("snap")
    increment_count("snap")
    result = increment_count("snap")
    assert result == 3
    assert get_count("snap") == 3


def test_increment_count_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        increment_count("ghost")


def test_get_count_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        get_count("ghost")


def test_reset_count_sets_to_zero():
    _save("snap")
    increment_count("snap")
    increment_count("snap")
    reset_count("snap")
    assert get_count("snap") == 0


def test_reset_count_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        reset_count("ghost")


def test_list_counts_sorted_descending():
    _save("a")
    _save("b")
    _save("c")
    increment_count("b")
    increment_count("b")
    increment_count("c")
    entries = list_counts()
    names = [e["name"] for e in entries]
    assert names.index("b") < names.index("c")


def test_list_counts_empty_when_no_data():
    assert list_counts() == []


def test_counts_are_independent_per_snapshot():
    _save("x")
    _save("y")
    increment_count("x")
    increment_count("x")
    increment_count("y")
    assert get_count("x") == 2
    assert get_count("y") == 1
