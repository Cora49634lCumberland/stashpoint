"""Tests for stashpoint.pin module."""

from __future__ import annotations

import os
import pytest

from stashpoint.pin import (
    SnapshotNotFoundError,
    get_pinned,
    is_pinned,
    pin_snapshot,
    unpin_snapshot,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _make_snapshot(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_pin_snapshot_returns_list(isolated_stash):
    _make_snapshot("snap1")
    result = pin_snapshot("snap1")
    assert "snap1" in result


def test_pin_snapshot_is_idempotent(isolated_stash):
    _make_snapshot("snap1")
    pin_snapshot("snap1")
    pins = pin_snapshot("snap1")
    assert pins.count("snap1") == 1


def test_pin_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        pin_snapshot("ghost")


def test_unpin_snapshot_removes_pin(isolated_stash):
    _make_snapshot("snap1")
    pin_snapshot("snap1")
    pins = unpin_snapshot("snap1")
    assert "snap1" not in pins


def test_unpin_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        unpin_snapshot("ghost")


def test_is_pinned_true(isolated_stash):
    _make_snapshot("snap1")
    pin_snapshot("snap1")
    assert is_pinned("snap1") is True


def test_is_pinned_false(isolated_stash):
    _make_snapshot("snap1")
    assert is_pinned("snap1") is False


def test_get_pinned_returns_all(isolated_stash):
    _make_snapshot("a")
    _make_snapshot("b")
    pin_snapshot("a")
    pin_snapshot("b")
    pins = get_pinned()
    assert set(pins) == {"a", "b"}


def test_get_pinned_empty_when_no_pins(isolated_stash):
    assert get_pinned() == []


def test_pin_multiple_snapshots(isolated_stash):
    for name in ["x", "y", "z"]:
        _make_snapshot(name)
        pin_snapshot(name)
    assert set(get_pinned()) == {"x", "y", "z"}
