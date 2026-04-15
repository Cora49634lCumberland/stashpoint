"""Tests for stashpoint/lock.py"""

import json
import pytest

from stashpoint.lock import (
    SnapshotAlreadyLockedError,
    SnapshotNotFoundError,
    SnapshotNotLockedError,
    assert_not_locked,
    get_locked_snapshots,
    is_locked,
    lock_snapshot,
    unlock_snapshot,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _make_snapshot(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "value"})


def test_lock_snapshot_returns_list(isolated_stash):
    _make_snapshot("prod")
    result = lock_snapshot("prod")
    assert "prod" in result


def test_lock_snapshot_is_idempotent_raises(isolated_stash):
    _make_snapshot("prod")
    lock_snapshot("prod")
    with pytest.raises(SnapshotAlreadyLockedError):
        lock_snapshot("prod")


def test_lock_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        lock_snapshot("ghost")


def test_unlock_snapshot_removes_from_list(isolated_stash):
    _make_snapshot("staging")
    lock_snapshot("staging")
    result = unlock_snapshot("staging")
    assert "staging" not in result


def test_unlock_not_locked_raises(isolated_stash):
    _make_snapshot("staging")
    with pytest.raises(SnapshotNotLockedError):
        unlock_snapshot("staging")


def test_is_locked_true_after_lock(isolated_stash):
    _make_snapshot("dev")
    lock_snapshot("dev")
    assert is_locked("dev") is True


def test_is_locked_false_when_not_locked(isolated_stash):
    _make_snapshot("dev")
    assert is_locked("dev") is False


def test_get_locked_snapshots_empty(isolated_stash):
    assert get_locked_snapshots() == []


def test_get_locked_snapshots_multiple(isolated_stash):
    _make_snapshot("a")
    _make_snapshot("b")
    lock_snapshot("a")
    lock_snapshot("b")
    locked = get_locked_snapshots()
    assert set(locked) == {"a", "b"}


def test_assert_not_locked_passes_when_unlocked(isolated_stash):
    _make_snapshot("safe")
    assert_not_locked("safe")  # should not raise


def test_assert_not_locked_raises_when_locked(isolated_stash):
    _make_snapshot("safe")
    lock_snapshot("safe")
    with pytest.raises(SnapshotAlreadyLockedError):
        assert_not_locked("safe")


def test_locks_persisted_to_disk(isolated_stash):
    _make_snapshot("persist")
    lock_snapshot("persist")
    locks_file = isolated_stash / "locks.json"
    assert locks_file.exists()
    data = json.loads(locks_file.read_text())
    assert "persist" in data
