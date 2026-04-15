"""Tests for stashpoint.merge module."""

import os
import pytest
from unittest.mock import patch
from stashpoint.merge import merge_snapshots, get_merge_conflicts, SnapshotNotFoundError
from stashpoint import storage


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    stash_file = tmp_path / "snapshots.json"
    monkeypatch.setattr(storage, "get_stash_path", lambda: stash_file)
    yield stash_file


def _save(name, data):
    storage.save_snapshot(name, data)


# ---------------------------------------------------------------------------
# merge_snapshots
# ---------------------------------------------------------------------------

def test_merge_two_snapshots_last_wins():
    _save("a", {"FOO": "1", "BAR": "from_a"})
    _save("b", {"BAR": "from_b", "BAZ": "3"})
    merged = merge_snapshots(["a", "b"], target_name="merged")
    assert merged == {"FOO": "1", "BAR": "from_b", "BAZ": "3"}


def test_merge_two_snapshots_first_wins():
    _save("a", {"FOO": "1", "BAR": "from_a"})
    _save("b", {"BAR": "from_b", "BAZ": "3"})
    merged = merge_snapshots(["a", "b"], target_name="merged", strategy="first-wins")
    assert merged["BAR"] == "from_a"


def test_merge_saves_to_storage():
    _save("x", {"KEY": "val"})
    merge_snapshots(["x"], target_name="result")
    loaded = storage.load_snapshot("result")
    assert loaded == {"KEY": "val"}


def test_merge_missing_source_raises():
    with pytest.raises(SnapshotNotFoundError, match="ghost"):
        merge_snapshots(["ghost"], target_name="out")


def test_merge_existing_target_raises_without_overwrite():
    _save("src", {"A": "1"})
    _save("existing", {"B": "2"})
    with pytest.raises(ValueError, match="already exists"):
        merge_snapshots(["src"], target_name="existing", overwrite=False)


def test_merge_existing_target_succeeds_with_overwrite():
    _save("src", {"A": "1"})
    _save("existing", {"B": "2"})
    merged = merge_snapshots(["src"], target_name="existing", overwrite=True)
    assert merged == {"A": "1"}


def test_merge_empty_sources_raises():
    with pytest.raises(ValueError):
        merge_snapshots([], target_name="out")


def test_merge_unknown_strategy_raises():
    _save("s", {"K": "v"})
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_snapshots(["s"], target_name="out", strategy="random")


# ---------------------------------------------------------------------------
# get_merge_conflicts
# ---------------------------------------------------------------------------

def test_no_conflicts_when_keys_disjoint():
    _save("a", {"FOO": "1"})
    _save("b", {"BAR": "2"})
    assert get_merge_conflicts(["a", "b"]) == {}


def test_detects_conflicts_on_same_key_different_value():
    _save("a", {"X": "hello"})
    _save("b", {"X": "world"})
    conflicts = get_merge_conflicts(["a", "b"])
    assert "X" in conflicts
    assert set(conflicts["X"]) == {"hello", "world"}


def test_no_conflict_when_values_identical():
    _save("a", {"X": "same"})
    _save("b", {"X": "same"})
    conflicts = get_merge_conflicts(["a", "b"])
    assert conflicts == {}


def test_conflicts_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        get_merge_conflicts(["does_not_exist"])
