"""Tests for stashpoint.version."""

from __future__ import annotations

import pytest
from unittest.mock import patch

from stashpoint.version import (
    SnapshotNotFoundError,
    VersionNotFoundError,
    create_version,
    list_versions,
    get_version,
    restore_version,
    delete_version,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, vars_: dict):
    from stashpoint.storage import load_snapshots, save_snapshots
    snaps = load_snapshots()
    snaps[name] = vars_
    save_snapshots(snaps)


# ---------------------------------------------------------------------------

def test_create_version_returns_entry():
    _save("dev", {"FOO": "bar"})
    entry = create_version("dev", message="initial")
    assert entry["version"] == 1
    assert entry["message"] == "initial"
    assert entry["vars"] == {"FOO": "bar"}
    assert "timestamp" in entry


def test_create_version_increments_number():
    _save("dev", {"FOO": "1"})
    create_version("dev")
    _save("dev", {"FOO": "2"})
    entry = create_version("dev")
    assert entry["version"] == 2


def test_create_version_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        create_version("ghost")


def test_list_versions_newest_first():
    _save("dev", {"X": "1"})
    create_version("dev")
    _save("dev", {"X": "2"})
    create_version("dev")
    versions = list_versions("dev")
    assert [v["version"] for v in versions] == [2, 1]


def test_list_versions_empty_when_none():
    assert list_versions("nonexistent") == []


def test_get_version_returns_correct_entry():
    _save("dev", {"A": "1"})
    create_version("dev", message="v1")
    _save("dev", {"A": "2"})
    create_version("dev", message="v2")
    entry = get_version("dev", 1)
    assert entry["vars"] == {"A": "1"}
    assert entry["message"] == "v1"


def test_get_version_missing_raises():
    _save("dev", {})
    create_version("dev")
    with pytest.raises(VersionNotFoundError):
        get_version("dev", 99)


def test_restore_version_overwrites_active_snapshot():
    _save("dev", {"ENV": "staging"})
    create_version("dev")
    _save("dev", {"ENV": "production"})
    create_version("dev")

    restore_version("dev", 1)

    from stashpoint.storage import load_snapshots
    assert load_snapshots()["dev"] == {"ENV": "staging"}


def test_restore_version_missing_raises():
    _save("dev", {})
    create_version("dev")
    with pytest.raises(VersionNotFoundError):
        restore_version("dev", 42)


def test_delete_version_removes_entry():
    _save("dev", {"K": "v"})
    create_version("dev")
    _save("dev", {"K": "v2"})
    create_version("dev")
    remaining = delete_version("dev", 1)
    assert all(e["version"] != 1 for e in remaining)
    assert len(remaining) == 1


def test_delete_version_missing_raises():
    _save("dev", {})
    create_version("dev")
    with pytest.raises(VersionNotFoundError):
        delete_version("dev", 99)
