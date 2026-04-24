"""Tests for stashpoint.dependency."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.dependency import (
    CircularDependencyError,
    DependencyAlreadyExistsError,
    DependencyNotFoundError,
    SnapshotNotFoundError,
    add_dependency,
    get_dependencies,
    get_dependents,
    remove_dependency,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    storage.save_snapshot(name, data or {"KEY": "val"})


def test_add_dependency_returns_list():
    _save("a")
    _save("b")
    result = add_dependency("a", "b")
    assert result == ["b"]


def test_add_multiple_dependencies():
    _save("a")
    _save("b")
    _save("c")
    add_dependency("a", "b")
    result = add_dependency("a", "c")
    assert set(result) == {"b", "c"}


def test_add_dependency_missing_snapshot_raises():
    _save("a")
    with pytest.raises(SnapshotNotFoundError):
        add_dependency("a", "ghost")


def test_add_dependency_missing_name_raises():
    _save("b")
    with pytest.raises(SnapshotNotFoundError):
        add_dependency("ghost", "b")


def test_add_duplicate_dependency_raises():
    _save("a")
    _save("b")
    add_dependency("a", "b")
    with pytest.raises(DependencyAlreadyExistsError):
        add_dependency("a", "b")


def test_circular_dependency_raises():
    _save("a")
    _save("b")
    add_dependency("a", "b")
    with pytest.raises(CircularDependencyError):
        add_dependency("b", "a")


def test_circular_dependency_indirect_raises():
    _save("a")
    _save("b")
    _save("c")
    add_dependency("a", "b")
    add_dependency("b", "c")
    with pytest.raises(CircularDependencyError):
        add_dependency("c", "a")


def test_remove_dependency():
    _save("a")
    _save("b")
    add_dependency("a", "b")
    remaining = remove_dependency("a", "b")
    assert remaining == []


def test_remove_missing_dependency_raises():
    _save("a")
    _save("b")
    with pytest.raises(DependencyNotFoundError):
        remove_dependency("a", "b")


def test_get_dependencies_empty():
    _save("a")
    assert get_dependencies("a") == []


def test_get_dependents():
    _save("a")
    _save("b")
    _save("c")
    add_dependency("b", "a")
    add_dependency("c", "a")
    result = get_dependents("a")
    assert set(result) == {"b", "c"}


def test_get_dependents_empty():
    _save("a")
    assert get_dependents("a") == []
