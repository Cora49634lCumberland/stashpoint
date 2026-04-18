"""Tests for stashpoint.namespace."""

import pytest
from stashpoint import namespace as ns_mod
from stashpoint.storage import save_snapshot
from stashpoint.namespace import (
    create_namespace,
    delete_namespace,
    add_to_namespace,
    remove_from_namespace,
    list_namespaces,
    get_namespace,
    NamespaceAlreadyExistsError,
    NamespaceNotFoundError,
    SnapshotNotFoundError,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.namespace.get_stash_path", lambda: tmp_path)


def _save(name, data):
    save_snapshot(name, data)


def test_create_namespace_basic():
    result = create_namespace("prod")
    assert result == []


def test_create_namespace_duplicate_raises():
    create_namespace("prod")
    with pytest.raises(NamespaceAlreadyExistsError):
        create_namespace("prod")


def test_delete_namespace():
    create_namespace("staging")
    delete_namespace("staging")
    assert "staging" not in list_namespaces()


def test_delete_missing_namespace_raises():
    with pytest.raises(NamespaceNotFoundError):
        delete_namespace("ghost")


def test_add_snapshot_to_namespace():
    _save("snap1", {"KEY": "val"})
    create_namespace("dev")
    members = add_to_namespace("dev", "snap1")
    assert "snap1" in members


def test_add_missing_snapshot_raises():
    create_namespace("dev")
    with pytest.raises(SnapshotNotFoundError):
        add_to_namespace("dev", "nonexistent")


def test_add_to_missing_namespace_raises():
    _save("snap1", {"KEY": "val"})
    with pytest.raises(NamespaceNotFoundError):
        add_to_namespace("ghost", "snap1")


def test_add_duplicate_is_idempotent():
    _save("snap1", {"KEY": "val"})
    create_namespace("dev")
    add_to_namespace("dev", "snap1")
    members = add_to_namespace("dev", "snap1")
    assert members.count("snap1") == 1


def test_remove_snapshot_from_namespace():
    _save("snap1", {"KEY": "val"})
    create_namespace("dev")
    add_to_namespace("dev", "snap1")
    members = remove_from_namespace("dev", "snap1")
    assert "snap1" not in members


def test_list_namespaces_returns_all():
    create_namespace("a")
    create_namespace("b")
    data = list_namespaces()
    assert "a" in data and "b" in data


def test_get_namespace_returns_members():
    _save("snap1", {"K": "v"})
    create_namespace("ns")
    add_to_namespace("ns", "snap1")
    assert get_namespace("ns") == ["snap1"]


def test_get_missing_namespace_raises():
    with pytest.raises(NamespaceNotFoundError):
        get_namespace("missing")
