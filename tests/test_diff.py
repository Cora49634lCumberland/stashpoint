"""Tests for stashpoint.diff module."""

import os
import pytest
from unittest import mock

from stashpoint import storage
from stashpoint.diff import diff_snapshots, format_diff


@pytest.fixture
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path / "snapshots.json")


def test_diff_two_snapshots(isolated_stash):
    storage.save_snapshot("snap_a", {"FOO": "1", "BAR": "hello", "COMMON": "same"})
    storage.save_snapshot("snap_b", {"BAZ": "new", "BAR": "world", "COMMON": "same"})

    result = diff_snapshots("snap_a", "snap_b")

    assert result["added"] == {"BAZ": "new"}
    assert result["removed"] == {"FOO": "1"}
    assert result["changed"] == {"BAR": {"before": "hello", "after": "world"}}
    assert result["unchanged"] == {"COMMON": "same"}


def test_diff_against_current_env(isolated_stash, monkeypatch):
    storage.save_snapshot("snap_a", {"MY_VAR": "old_value", "ONLY_IN_SNAP": "yes"})
    monkeypatch.setenv("MY_VAR", "new_value")
    monkeypatch.setenv("ONLY_IN_ENV", "env_only")

    result = diff_snapshots("snap_a")

    assert result["label_b"] == "<current environment>"
    assert "ONLY_IN_ENV" in result["added"]
    assert "ONLY_IN_SNAP" in result["removed"]
    assert "MY_VAR" in result["changed"]
    assert result["changed"]["MY_VAR"]["before"] == "old_value"
    assert result["changed"]["MY_VAR"]["after"] == "new_value"


def test_diff_identical_snapshots(isolated_stash):
    data = {"X": "1", "Y": "2"}
    storage.save_snapshot("s1", data)
    storage.save_snapshot("s2", data)

    result = diff_snapshots("s1", "s2")

    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == data


def test_diff_missing_snapshot_a_raises(isolated_stash):
    storage.save_snapshot("exists", {"A": "1"})
    with pytest.raises(KeyError, match="'missing' not found"):
        diff_snapshots("missing", "exists")


def test_diff_missing_snapshot_b_raises(isolated_stash):
    storage.save_snapshot("exists", {"A": "1"})
    with pytest.raises(KeyError, match="'ghost' not found"):
        diff_snapshots("exists", "ghost")


def test_format_diff_shows_changes(isolated_stash):
    storage.save_snapshot("a", {"FOO": "1", "KEEP": "same"})
    storage.save_snapshot("b", {"BAR": "2", "KEEP": "same"})

    result = diff_snapshots("a", "b")
    output = format_diff(result)

    assert "[+] Added" in output
    assert "BAR=2" in output
    assert "[-] Removed" in output
    assert "FOO=1" in output
    assert "Comparing 'a' → 'b'" in output


def test_format_diff_no_differences(isolated_stash):
    storage.save_snapshot("x", {"A": "1"})
    storage.save_snapshot("y", {"A": "1"})

    result = diff_snapshots("x", "y")
    output = format_diff(result)

    assert "No differences found" in output
