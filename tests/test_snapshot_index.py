"""Tests for stashpoint.snapshot_index."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.snapshot_index import (
    SnapshotNotFoundError,
    build_index,
    get_index,
    invalidate_index,
    keys_in_snapshot,
    snapshots_containing_key,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, env: dict) -> None:
    from stashpoint.storage import save_snapshot
    save_snapshot(name, env)


def test_build_index_returns_key_to_snapshot_mapping():
    _save("alpha", {"FOO": "1", "BAR": "2"})
    _save("beta", {"FOO": "99", "BAZ": "3"})
    index = build_index()
    assert "alpha" in index["FOO"]
    assert "beta" in index["FOO"]
    assert index["BAR"] == ["alpha"]
    assert index["BAZ"] == ["beta"]


def test_build_index_persists_to_disk(tmp_path):
    _save("snap", {"KEY": "val"})
    build_index()
    assert (tmp_path / "snapshot_index.json").exists()


def test_get_index_builds_when_missing():
    _save("snap", {"X": "1"})
    invalidate_index()
    index = get_index()
    assert "X" in index


def test_get_index_uses_cache(tmp_path):
    _save("snap", {"A": "1"})
    build_index()
    # Add another snapshot without rebuilding
    _save("snap2", {"B": "2"})
    index = get_index()
    # Cache should not include new key yet
    assert "B" not in index


def test_snapshots_containing_key_returns_names():
    _save("s1", {"ENV": "dev"})
    _save("s2", {"ENV": "prod", "PORT": "8080"})
    build_index()
    result = snapshots_containing_key("ENV")
    assert "s1" in result
    assert "s2" in result


def test_snapshots_containing_key_returns_empty_for_unknown():
    _save("s1", {"FOO": "bar"})
    build_index()
    assert snapshots_containing_key("NONEXISTENT") == []


def test_keys_in_snapshot_returns_all_keys():
    _save("mysnap", {"A": "1", "B": "2", "C": "3"})
    keys = keys_in_snapshot("mysnap")
    assert set(keys) == {"A", "B", "C"}


def test_keys_in_snapshot_missing_raises():
    with pytest.raises(SnapshotNotFoundError):
        keys_in_snapshot("ghost")


def test_invalidate_index_removes_file(tmp_path):
    _save("s", {"K": "v"})
    build_index()
    assert (tmp_path / "snapshot_index.json").exists()
    invalidate_index()
    assert not (tmp_path / "snapshot_index.json").exists()


def test_invalidate_index_noop_when_no_file():
    # Should not raise if index file doesn't exist
    invalidate_index()
