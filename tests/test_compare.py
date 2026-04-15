"""Tests for stashpoint.compare module."""

import os
import pytest
from unittest.mock import patch

from stashpoint.compare import compare_snapshots, format_compare, SnapshotNotFoundError
from stashpoint import storage


@pytest.fixture()
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


def _save(name, data, isolated_stash):
    storage.save_snapshot(name, data)


def test_compare_two_snapshots(isolated_stash):
    _save("a", {"FOO": "1", "BAR": "shared"}, isolated_stash)
    _save("b", {"BAZ": "2", "BAR": "shared"}, isolated_stash)
    result = compare_snapshots(["a", "b"])
    assert result["shared"] == ["BAR"]
    assert "FOO" in result["unique"]["a"]
    assert "BAZ" in result["unique"]["b"]


def test_compare_all_keys_present(isolated_stash):
    _save("x", {"A": "1", "B": "2"}, isolated_stash)
    _save("y", {"B": "3", "C": "4"}, isolated_stash)
    result = compare_snapshots(["x", "y"])
    assert set(result["keys"]) == {"A", "B", "C"}


def test_compare_missing_snapshot_raises(isolated_stash):
    _save("exists", {"K": "v"}, isolated_stash)
    with pytest.raises(SnapshotNotFoundError):
        compare_snapshots(["exists", "ghost"])


def test_compare_requires_at_least_two():
    with pytest.raises(ValueError):
        compare_snapshots(["only_one"])


def test_compare_identical_snapshots(isolated_stash):
    _save("p", {"X": "1"}, isolated_stash)
    _save("q", {"X": "1"}, isolated_stash)
    result = compare_snapshots(["p", "q"])
    assert result["shared"] == ["X"]
    assert result["unique"]["p"] == []
    assert result["unique"]["q"] == []


def test_compare_three_snapshots(isolated_stash):
    _save("s1", {"A": "1", "COMMON": "yes"}, isolated_stash)
    _save("s2", {"B": "2", "COMMON": "yes"}, isolated_stash)
    _save("s3", {"C": "3", "COMMON": "yes"}, isolated_stash)
    result = compare_snapshots(["s1", "s2", "s3"])
    assert result["shared"] == ["COMMON"]
    assert "A" in result["unique"]["s1"]
    assert "B" in result["unique"]["s2"]
    assert "C" in result["unique"]["s3"]


def test_format_compare_contains_snapshot_names(isolated_stash):
    _save("alpha", {"KEY": "val"}, isolated_stash)
    _save("beta", {"KEY": "other"}, isolated_stash)
    result = compare_snapshots(["alpha", "beta"])
    output = format_compare(result)
    assert "alpha" in output
    assert "beta" in output
    assert "KEY" in output


def test_format_compare_missing_value_shown(isolated_stash):
    _save("m", {"ONLY_M": "1"}, isolated_stash)
    _save("n", {"ONLY_N": "2"}, isolated_stash)
    result = compare_snapshots(["m", "n"])
    output = format_compare(result)
    assert "<missing>" in output
