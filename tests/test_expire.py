"""Tests for stashpoint.expire."""

import time
import pytest
from unittest.mock import patch

from stashpoint import storage
from stashpoint.expire import (
    SnapshotNotFoundError,
    set_expiry,
    remove_expiry,
    get_expiry,
    is_expired,
    list_expiring,
    purge_expired,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    import stashpoint.expire as expire_mod
    monkeypatch.setattr(expire_mod, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict = None):
    from stashpoint.storage import save_snapshot
    save_snapshot(name, data or {"KEY": "val"})


def test_set_expiry_returns_timestamp():
    _save("snap")
    before = time.time()
    ts = set_expiry("snap", 60)
    after = time.time()
    assert before + 59 <= ts <= after + 61


def test_set_expiry_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_expiry("ghost", 60)


def test_get_expiry_returns_none_when_not_set():
    _save("snap")
    assert get_expiry("snap") is None


def test_get_expiry_after_set():
    _save("snap")
    set_expiry("snap", 100)
    ts = get_expiry("snap")
    assert ts is not None
    assert ts > time.time()


def test_remove_expiry_clears_entry():
    _save("snap")
    set_expiry("snap", 100)
    remove_expiry("snap")
    assert get_expiry("snap") is None


def test_is_expired_false_for_future():
    _save("snap")
    set_expiry("snap", 9999)
    assert is_expired("snap") is False


def test_is_expired_true_for_past():
    _save("snap")
    set_expiry("snap", -1)  # already in the past
    assert is_expired("snap") is True


def test_is_expired_false_when_no_expiry():
    _save("snap")
    assert is_expired("snap") is False


def test_list_expiring_returns_sorted_entries():
    _save("a")
    _save("b")
    set_expiry("b", 200)
    set_expiry("a", 100)
    entries = list_expiring()
    assert [e["name"] for e in entries] == ["a", "b"]


def test_purge_expired_removes_expired_snapshots():
    _save("old")
    _save("fresh")
    set_expiry("old", -1)
    set_expiry("fresh", 9999)
    purged = purge_expired()
    assert "old" in purged
    assert "fresh" not in purged
    from stashpoint.storage import load_snapshot
    assert load_snapshot("old") is None
    assert load_snapshot("fresh") is not None


def test_purge_expired_returns_empty_when_none_expired():
    _save("snap")
    set_expiry("snap", 9999)
    assert purge_expired() == []
