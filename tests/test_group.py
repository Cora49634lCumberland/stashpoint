"""Tests for stashpoint.group."""

import pytest
from stashpoint import storage
from stashpoint.group import (
    create_group, delete_group, get_group, list_groups, add_to_group,
    GroupNotFoundError, GroupAlreadyExistsError, SnapshotNotFoundError,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    import stashpoint.group as gmod
    monkeypatch.setattr(gmod, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name, data):
    from stashpoint.storage import save_snapshot
    save_snapshot(name, data)


def test_create_group_basic():
    _save("snap1", {"A": "1"})
    _save("snap2", {"B": "2"})
    members = create_group("mygroup", ["snap1", "snap2"])
    assert members == ["snap1", "snap2"]


def test_create_group_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        create_group("g", ["nonexistent"])


def test_create_group_duplicate_raises():
    _save("snap1", {"A": "1"})
    create_group("g", ["snap1"])
    with pytest.raises(GroupAlreadyExistsError):
        create_group("g", ["snap1"])


def test_get_group_returns_members():
    _save("snap1", {"A": "1"})
    create_group("g", ["snap1"])
    assert get_group("g") == ["snap1"]


def test_get_group_missing_raises():
    with pytest.raises(GroupNotFoundError):
        get_group("nope")


def test_delete_group():
    _save("snap1", {"A": "1"})
    create_group("g", ["snap1"])
    delete_group("g")
    assert "g" not in list_groups()


def test_delete_missing_group_raises():
    with pytest.raises(GroupNotFoundError):
        delete_group("ghost")


def test_list_groups_empty():
    assert list_groups() == {}


def test_list_groups_returns_all():
    _save("s1", {"X": "1"})
    _save("s2", {"Y": "2"})
    create_group("g1", ["s1"])
    create_group("g2", ["s2"])
    groups = list_groups()
    assert "g1" in groups
    assert "g2" in groups


def test_add_to_group():
    _save("s1", {"A": "1"})
    _save("s2", {"B": "2"})
    create_group("g", ["s1"])
    members = add_to_group("g", "s2")
    assert "s2" in members


def test_add_to_group_idempotent():
    _save("s1", {"A": "1"})
    create_group("g", ["s1"])
    add_to_group("g", "s1")
    assert get_group("g").count("s1") == 1


def test_add_to_missing_group_raises():
    _save("s1", {"A": "1"})
    with pytest.raises(GroupNotFoundError):
        add_to_group("ghost", "s1")
