import pytest
from pathlib import Path
from unittest.mock import patch
from stashpoint.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    SnapshotNotFoundError,
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


def _save(name, data):
    save_snapshot(name, data)


def test_add_favorite_returns_list(isolated_stash):
    _save("dev", {"A": "1"})
    result = add_favorite("dev")
    assert "dev" in result


def test_add_favorite_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        add_favorite("ghost")


def test_add_duplicate_favorite_raises(isolated_stash):
    _save("dev", {"A": "1"})
    add_favorite("dev")
    with pytest.raises(FavoriteAlreadyExistsError):
        add_favorite("dev")


def test_remove_favorite(isolated_stash):
    _save("dev", {"A": "1"})
    add_favorite("dev")
    result = remove_favorite("dev")
    assert "dev" not in result


def test_remove_nonexistent_favorite_raises(isolated_stash):
    with pytest.raises(FavoriteNotFoundError):
        remove_favorite("ghost")


def test_list_favorites_empty(isolated_stash):
    assert list_favorites() == []


def test_list_favorites_multiple(isolated_stash):
    _save("dev", {"A": "1"})
    _save("prod", {"B": "2"})
    add_favorite("dev")
    add_favorite("prod")
    result = list_favorites()
    assert "dev" in result
    assert "prod" in result


def test_is_favorite_true(isolated_stash):
    _save("dev", {"A": "1"})
    add_favorite("dev")
    assert is_favorite("dev") is True


def test_is_favorite_false(isolated_stash):
    assert is_favorite("dev") is False
