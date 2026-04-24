"""Tests for stashpoint.status module."""

from __future__ import annotations

import json
import pytest

from stashpoint.status import (
    SnapshotNotFoundError,
    InvalidStatusError,
    set_status,
    get_status,
    remove_status,
    list_by_status,
)
from stashpoint.storage import save_snapshot, get_stash_path


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.STASH_DIR", tmp_path)
    monkeypatch.setattr("stashpoint.status.get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_set_status_returns_status(isolated_stash):
    _save("snap1")
    result = set_status("snap1", "active")
    assert result == "active"


def test_get_status_returns_stored(isolated_stash):
    _save("snap1")
    set_status("snap1", "draft")
    assert get_status("snap1") == "draft"


def test_get_status_returns_none_when_not_set(isolated_stash):
    _save("snap1")
    assert get_status("snap1") is None


def test_set_status_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_status("ghost", "active")


def test_set_status_invalid_status_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(InvalidStatusError):
        set_status("snap1", "unknown")


def test_set_status_overwrites_existing(isolated_stash):
    _save("snap1")
    set_status("snap1", "draft")
    set_status("snap1", "deprecated")
    assert get_status("snap1") == "deprecated"


def test_remove_status_clears_entry(isolated_stash):
    _save("snap1")
    set_status("snap1", "active")
    remove_status("snap1")
    assert get_status("snap1") is None


def test_remove_status_noop_when_not_set(isolated_stash):
    _save("snap1")
    remove_status("snap1")  # should not raise


def test_list_by_status_returns_matching(isolated_stash):
    _save("a")
    _save("b")
    _save("c")
    set_status("a", "active")
    set_status("b", "active")
    set_status("c", "deprecated")
    result = list_by_status("active")
    assert sorted(result) == ["a", "b"]


def test_list_by_status_empty_when_none_match(isolated_stash):
    _save("snap1")
    set_status("snap1", "draft")
    assert list_by_status("active") == []


def test_list_by_status_invalid_raises(isolated_stash):
    with pytest.raises(InvalidStatusError):
        list_by_status("bogus")
