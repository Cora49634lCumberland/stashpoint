"""Tests for stashpoint.watch drift detection."""

import os
import pytest
from unittest.mock import patch
from stashpoint.watch import check_drift, format_drift, SnapshotNotFoundError
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name, data):
    save_snapshot(name, data)


def test_no_drift_when_env_matches(monkeypatch):
    _save("snap", {"FOO": "bar"})
    monkeypatch.setenv("FOO", "bar")
    result = check_drift("snap")
    assert not result.has_drift


def test_detects_changed_value(monkeypatch):
    _save("snap", {"FOO": "bar"})
    monkeypatch.setenv("FOO", "baz")
    result = check_drift("snap")
    assert result.has_drift
    assert "FOO" in result.changed
    assert result.changed["FOO"]["snapshot"] == "bar"
    assert result.changed["FOO"]["current"] == "baz"


def test_detects_removed_key(monkeypatch):
    _save("snap", {"MISSING_KEY": "val"})
    monkeypatch.delenv("MISSING_KEY", raising=False)
    result = check_drift("snap")
    assert "MISSING_KEY" in result.removed


def test_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        check_drift("nonexistent")


def test_keys_filter_limits_scope(monkeypatch):
    _save("snap", {"FOO": "1", "BAR": "2"})
    monkeypatch.setenv("FOO", "changed")
    monkeypatch.setenv("BAR", "changed")
    result = check_drift("snap", keys=["FOO"])
    assert "FOO" in result.changed
    assert "BAR" not in result.changed


def test_format_drift_no_drift(monkeypatch):
    _save("snap", {"X": "1"})
    monkeypatch.setenv("X", "1")
    result = check_drift("snap")
    output = format_drift(result)
    assert "No drift" in output


def test_format_drift_shows_changes(monkeypatch):
    _save("snap", {"X": "old"})
    monkeypatch.setenv("X", "new")
    result = check_drift("snap")
    output = format_drift(result)
    assert "old" in output
    assert "new" in output


def test_format_drift_shows_removed_key(monkeypatch):
    """format_drift should mention keys present in snapshot but missing from env."""
    _save("snap", {"GONE_KEY": "somevalue"})
    monkeypatch.delenv("GONE_KEY", raising=False)
    result = check_drift("snap")
    output = format_drift(result)
    assert "GONE_KEY" in output
