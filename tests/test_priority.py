"""Tests for stashpoint.priority."""

import pytest
from unittest.mock import patch
from stashpoint import priority as P
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.priority.load_snapshot",
                        lambda name: {"KEY": "val"} if name in _snapshots else None)
    yield


_snapshots = set()


@pytest.fixture(autouse=True)
def reset_snapshots():
    _snapshots.clear()
    yield
    _snapshots.clear()


def _save(name):
    _snapshots.add(name)


def test_set_priority_returns_priority(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    _save("snap1")
    result = P.set_priority("snap1", "high")
    assert result == "high"


def test_get_priority_returns_stored(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    _save("snap1")
    P.set_priority("snap1", "critical")
    assert P.get_priority("snap1") == "critical"


def test_get_priority_returns_none_when_not_set(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    assert P.get_priority("nonexistent") is None


def test_set_priority_missing_snapshot_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    with pytest.raises(P.SnapshotNotFoundError):
        P.set_priority("ghost", "low")


def test_set_invalid_priority_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    _save("snap1")
    with pytest.raises(P.InvalidPriorityError):
        P.set_priority("snap1", "ultra")


def test_remove_priority(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    _save("snap1")
    P.set_priority("snap1", "low")
    P.remove_priority("snap1")
    assert P.get_priority("snap1") is None


def test_remove_priority_noop_when_not_set(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    P.remove_priority("snap1")  # should not raise


def test_list_by_priority(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    _save("a")
    _save("b")
    _save("c")
    P.set_priority("a", "high")
    P.set_priority("b", "low")
    P.set_priority("c", "high")
    result = P.list_by_priority("high")
    assert set(result) == {"a", "c"}


def test_list_by_invalid_priority_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.priority.get_stash_path", lambda: tmp_path)
    with pytest.raises(P.InvalidPriorityError):
        P.list_by_priority("mega")
