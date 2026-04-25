"""Tests for stashpoint.checkpoint."""

from __future__ import annotations

import pytest

from stashpoint.checkpoint import (
    CheckpointAlreadyExistsError,
    CheckpointNotFoundError,
    SnapshotNotFoundError,
    create_checkpoint,
    get_checkpoint,
    get_checkpoints,
    remove_checkpoint,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_create_checkpoint_returns_entry():
    _save("snap1")
    entry = create_checkpoint("snap1", "v1")
    assert entry["snapshot"] == "snap1"
    assert entry["checkpoint"] == "v1"
    assert isinstance(entry["created_at"], float)


def test_create_checkpoint_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        create_checkpoint("ghost", "v1")


def test_create_checkpoint_duplicate_raises():
    _save("snap1")
    create_checkpoint("snap1", "v1")
    with pytest.raises(CheckpointAlreadyExistsError):
        create_checkpoint("snap1", "v1")


def test_get_checkpoints_returns_ordered_list():
    _save("snap1")
    create_checkpoint("snap1", "alpha")
    create_checkpoint("snap1", "beta")
    entries = get_checkpoints("snap1")
    assert len(entries) == 2
    assert entries[0]["checkpoint"] == "alpha"
    assert entries[1]["checkpoint"] == "beta"


def test_get_checkpoints_empty_for_unknown_snapshot():
    entries = get_checkpoints("no-such")
    assert entries == []


def test_get_checkpoint_returns_entry():
    _save("snap1")
    create_checkpoint("snap1", "v1")
    entry = get_checkpoint("snap1", "v1")
    assert entry is not None
    assert entry["checkpoint"] == "v1"


def test_get_checkpoint_returns_none_for_missing():
    _save("snap1")
    assert get_checkpoint("snap1", "nope") is None


def test_remove_checkpoint_deletes_entry():
    _save("snap1")
    create_checkpoint("snap1", "v1")
    remove_checkpoint("snap1", "v1")
    assert get_checkpoint("snap1", "v1") is None


def test_remove_checkpoint_missing_raises():
    _save("snap1")
    with pytest.raises(CheckpointNotFoundError):
        remove_checkpoint("snap1", "ghost")


def test_checkpoints_are_isolated_per_snapshot():
    _save("snap1")
    _save("snap2")
    create_checkpoint("snap1", "shared")
    assert get_checkpoints("snap2") == []
