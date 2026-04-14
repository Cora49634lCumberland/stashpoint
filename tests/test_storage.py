"""Tests for stashpoint.storage module."""

import json
import pytest
from pathlib import Path

from stashpoint.storage import (
    delete_snapshot,
    list_snapshot_names,
    load_snapshot,
    load_snapshots,
    save_snapshot,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    """Redirect stash storage to a temporary directory for each test."""
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))


def test_save_and_load_snapshot():
    save_snapshot("dev", {"DEBUG": "true", "PORT": "8080"})
    result = load_snapshot("dev")
    assert result == {"DEBUG": "true", "PORT": "8080"}


def test_load_missing_snapshot_returns_none():
    assert load_snapshot("nonexistent") is None


def test_load_snapshots_empty_when_no_file():
    assert load_snapshots() == {}


def test_save_snapshot_overwrites_existing():
    save_snapshot("dev", {"KEY": "old"})
    save_snapshot("dev", {"KEY": "new"})
    assert load_snapshot("dev") == {"KEY": "new"}


def test_delete_snapshot_returns_true_on_success():
    save_snapshot("staging", {"ENV": "staging"})
    assert delete_snapshot("staging") is True
    assert load_snapshot("staging") is None


def test_delete_snapshot_returns_false_when_missing():
    assert delete_snapshot("ghost") is False


def test_list_snapshot_names_sorted():
    save_snapshot("prod", {})
    save_snapshot("dev", {})
    save_snapshot("staging", {})
    assert list_snapshot_names() == ["dev", "prod", "staging"]


def test_snapshots_persisted_to_json(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    save_snapshot("ci", {"CI": "true"})
    stash_file = tmp_path / "snapshots.json"
    assert stash_file.exists()
    data = json.loads(stash_file.read_text())
    assert data["ci"] == {"CI": "true"}
