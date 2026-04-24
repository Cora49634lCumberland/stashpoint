"""Tests for stashpoint.access module."""

from __future__ import annotations

import pytest

from stashpoint.access import (
    AccessEntryNotFoundError,
    SnapshotNotFoundError,
    check_access,
    get_access,
    remove_access,
    set_access,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "val"})


def test_set_access_returns_principal_permissions():
    _save("snap1")
    result = set_access("snap1", "alice", ["read"])
    assert result["alice"] == ["read"]


def test_set_access_multiple_permissions():
    _save("snap1")
    result = set_access("snap1", "bob", ["read", "write"])
    assert set(result["bob"]) == {"read", "write"}


def test_set_access_ignores_invalid_permissions():
    _save("snap1")
    result = set_access("snap1", "alice", ["read", "delete", "admin"])
    assert result["alice"] == ["read"]


def test_set_access_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_access("ghost", "alice", ["read"])


def test_get_access_returns_all_entries():
    _save("snap1")
    set_access("snap1", "alice", ["read"])
    set_access("snap1", "bob", ["write"])
    entries = get_access("snap1")
    assert "alice" in entries
    assert "bob" in entries


def test_get_access_empty_when_none_set():
    _save("snap1")
    assert get_access("snap1") == {}


def test_remove_access_deletes_entry():
    _save("snap1")
    set_access("snap1", "alice", ["read"])
    remove_access("snap1", "alice")
    entries = get_access("snap1")
    assert "alice" not in entries


def test_remove_access_missing_entry_raises():
    _save("snap1")
    with pytest.raises(AccessEntryNotFoundError):
        remove_access("snap1", "nobody")


def test_check_access_returns_true_when_permitted():
    _save("snap1")
    set_access("snap1", "alice", ["read"])
    assert check_access("snap1", "alice", "read") is True


def test_check_access_returns_false_when_not_permitted():
    _save("snap1")
    set_access("snap1", "alice", ["read"])
    assert check_access("snap1", "alice", "write") is False


def test_check_access_returns_false_for_unknown_principal():
    _save("snap1")
    assert check_access("snap1", "ghost", "read") is False


def test_set_access_overwrites_existing_entry():
    _save("snap1")
    set_access("snap1", "alice", ["read"])
    set_access("snap1", "alice", ["write"])
    entries = get_access("snap1")
    assert entries["alice"] == ["write"]
