"""Tests for stashpoint.metadata."""

import pytest

from stashpoint.metadata import (
    MetadataKeyNotFoundError,
    SnapshotNotFoundError,
    get_all_metadata,
    get_metadata,
    remove_metadata,
    set_metadata,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "val"})


def test_set_metadata_returns_dict(isolated_stash):
    _save("snap")
    result = set_metadata("snap", "author", "alice")
    assert result == {"author": "alice"}


def test_set_metadata_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_metadata("ghost", "k", "v")


def test_set_metadata_multiple_keys(isolated_stash):
    _save("snap")
    set_metadata("snap", "env", "production")
    result = set_metadata("snap", "owner", "bob")
    assert result["env"] == "production"
    assert result["owner"] == "bob"


def test_set_metadata_overwrites_existing_key(isolated_stash):
    _save("snap")
    set_metadata("snap", "version", "1")
    result = set_metadata("snap", "version", "2")
    assert result["version"] == "2"


def test_get_metadata_returns_stored_value(isolated_stash):
    _save("snap")
    set_metadata("snap", "team", "backend")
    assert get_metadata("snap", "team") == "backend"


def test_get_metadata_missing_key_raises(isolated_stash):
    _save("snap")
    with pytest.raises(MetadataKeyNotFoundError):
        get_metadata("snap", "nonexistent")


def test_get_metadata_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        get_metadata("ghost", "k")


def test_remove_metadata_returns_remaining(isolated_stash):
    _save("snap")
    set_metadata("snap", "a", "1")
    set_metadata("snap", "b", "2")
    remaining = remove_metadata("snap", "a")
    assert "a" not in remaining
    assert remaining["b"] == "2"


def test_remove_metadata_missing_key_raises(isolated_stash):
    _save("snap")
    with pytest.raises(MetadataKeyNotFoundError):
        remove_metadata("snap", "nope")


def test_remove_metadata_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        remove_metadata("ghost", "k")


def test_get_all_metadata_empty_when_none_set(isolated_stash):
    _save("snap")
    assert get_all_metadata("snap") == {}


def test_get_all_metadata_returns_all_keys(isolated_stash):
    _save("snap")
    set_metadata("snap", "x", "10")
    set_metadata("snap", "y", "20")
    data = get_all_metadata("snap")
    assert data == {"x": "10", "y": "20"}


def test_get_all_metadata_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        get_all_metadata("ghost")
