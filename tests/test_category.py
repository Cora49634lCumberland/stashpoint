"""Tests for stashpoint.category."""

from __future__ import annotations

import pytest

from stashpoint.category import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    SnapshotNotFoundError,
    add_to_category,
    create_category,
    delete_category,
    get_category,
    get_snapshot_categories,
    list_categories,
    remove_from_category,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_create_category_basic():
    name = create_category("dev")
    assert name == "dev"
    assert "dev" in list_categories()


def test_create_category_duplicate_raises():
    create_category("staging")
    with pytest.raises(CategoryAlreadyExistsError):
        create_category("staging")


def test_delete_category():
    create_category("temp")
    delete_category("temp")
    assert "temp" not in list_categories()


def test_delete_missing_category_raises():
    with pytest.raises(CategoryNotFoundError):
        delete_category("nonexistent")


def test_add_to_category_returns_members():
    _save("snap1")
    create_category("prod")
    members = add_to_category("prod", "snap1")
    assert "snap1" in members


def test_add_to_category_missing_snapshot_raises():
    create_category("prod")
    with pytest.raises(SnapshotNotFoundError):
        add_to_category("prod", "ghost")


def test_add_to_category_missing_category_raises():
    _save("snap2")
    with pytest.raises(CategoryNotFoundError):
        add_to_category("nocat", "snap2")


def test_add_to_category_is_idempotent():
    _save("snap3")
    create_category("ci")
    add_to_category("ci", "snap3")
    members = add_to_category("ci", "snap3")
    assert members.count("snap3") == 1


def test_remove_from_category():
    _save("snap4")
    create_category("qa")
    add_to_category("qa", "snap4")
    members = remove_from_category("qa", "snap4")
    assert "snap4" not in members


def test_get_category_returns_members():
    _save("snap5")
    create_category("release")
    add_to_category("release", "snap5")
    members = get_category("release")
    assert "snap5" in members


def test_get_category_missing_raises():
    with pytest.raises(CategoryNotFoundError):
        get_category("missing")


def test_get_snapshot_categories():
    _save("snap6")
    create_category("alpha")
    create_category("beta")
    add_to_category("alpha", "snap6")
    add_to_category("beta", "snap6")
    cats = get_snapshot_categories("snap6")
    assert "alpha" in cats
    assert "beta" in cats


def test_list_categories_empty_initially():
    result = list_categories()
    assert result == {}
