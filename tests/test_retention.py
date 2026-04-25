"""Tests for stashpoint.retention."""

import pytest

from stashpoint import retention as ret_mod
from stashpoint.retention import (
    InvalidRetentionError,
    SnapshotNotFoundError,
    get_retention,
    list_retention,
    remove_retention,
    set_retention,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(ret_mod, "get_stash_path", lambda: tmp_path)
    from stashpoint import storage
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "val"})


def test_set_retention_returns_entry(isolated_stash):
    _save("snap1")
    entry = set_retention("snap1", "keep_last", 5)
    assert entry == {"policy": "keep_last", "value": 5}


def test_set_retention_keep_all_no_value(isolated_stash):
    _save("snap1")
    entry = set_retention("snap1", "keep_all")
    assert entry == {"policy": "keep_all"}
    assert "value" not in entry


def test_set_retention_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_retention("ghost", "keep_last", 3)


def test_set_retention_invalid_policy_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(InvalidRetentionError):
        set_retention("snap1", "forever", 1)


def test_set_retention_keep_last_without_value_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(InvalidRetentionError):
        set_retention("snap1", "keep_last")


def test_get_retention_returns_stored(isolated_stash):
    _save("snap1")
    set_retention("snap1", "keep_days", 30)
    entry = get_retention("snap1")
    assert entry == {"policy": "keep_days", "value": 30}


def test_get_retention_returns_none_when_not_set(isolated_stash):
    _save("snap1")
    assert get_retention("snap1") is None


def test_remove_retention_clears_entry(isolated_stash):
    _save("snap1")
    set_retention("snap1", "keep_last", 10)
    remove_retention("snap1")
    assert get_retention("snap1") is None


def test_remove_retention_noop_when_not_set(isolated_stash):
    _save("snap1")
    remove_retention("snap1")  # should not raise


def test_list_retention_returns_all(isolated_stash):
    _save("a")
    _save("b")
    set_retention("a", "keep_last", 3)
    set_retention("b", "keep_all")
    policies = list_retention()
    assert "a" in policies
    assert "b" in policies
    assert policies["a"]["policy"] == "keep_last"
    assert policies["b"]["policy"] == "keep_all"


def test_list_retention_empty_when_none_set(isolated_stash):
    assert list_retention() == {}
