"""Tests for stashpoint.annotation."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.annotation import (
    AnnotationKeyNotFoundError,
    SnapshotNotFoundError,
    get_all_annotations,
    get_annotation,
    list_annotated_snapshots,
    remove_annotation,
    set_annotation,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict) -> None:
    from stashpoint.storage import save_snapshot
    save_snapshot(name, data)


def test_set_annotation_returns_dict(isolated_stash):
    _save("snap1", {"A": "1"})
    result = set_annotation("snap1", "env", "production")
    assert result == {"env": "production"}


def test_set_annotation_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_annotation("ghost", "k", "v")


def test_set_annotation_multiple_keys(isolated_stash):
    _save("snap2", {"X": "1"})
    set_annotation("snap2", "owner", "alice")
    set_annotation("snap2", "team", "platform")
    result = get_all_annotations("snap2")
    assert result == {"owner": "alice", "team": "platform"}


def test_set_annotation_overwrites_existing(isolated_stash):
    _save("snap3", {"X": "1"})
    set_annotation("snap3", "env", "staging")
    set_annotation("snap3", "env", "production")
    assert get_annotation("snap3", "env") == "production"


def test_get_annotation_returns_none_when_absent(isolated_stash):
    _save("snap4", {"X": "1"})
    assert get_annotation("snap4", "missing") is None


def test_get_annotation_returns_none_for_unknown_snapshot(isolated_stash):
    assert get_annotation("nobody", "key") is None


def test_remove_annotation_removes_key(isolated_stash):
    _save("snap5", {"X": "1"})
    set_annotation("snap5", "env", "dev")
    remaining = remove_annotation("snap5", "env")
    assert "env" not in remaining
    assert get_annotation("snap5", "env") is None


def test_remove_annotation_missing_key_raises(isolated_stash):
    _save("snap6", {"X": "1"})
    with pytest.raises(AnnotationKeyNotFoundError):
        remove_annotation("snap6", "nonexistent")


def test_get_all_annotations_empty_when_none_set(isolated_stash):
    _save("snap7", {"X": "1"})
    assert get_all_annotations("snap7") == {}


def test_list_annotated_snapshots_returns_only_annotated(isolated_stash):
    _save("a", {"K": "1"})
    _save("b", {"K": "2"})
    set_annotation("a", "note", "hello")
    result = list_annotated_snapshots()
    assert "a" in result
    assert "b" not in result


def test_list_annotated_snapshots_empty_when_none(isolated_stash):
    assert list_annotated_snapshots() == {}
