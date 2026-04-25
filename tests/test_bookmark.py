"""Tests for stashpoint.bookmark."""

from __future__ import annotations

import pytest

from stashpoint.bookmark import (
    add_bookmark,
    remove_bookmark,
    list_bookmarks,
    is_bookmarked,
    BookmarkAlreadyExistsError,
    BookmarkNotFoundError,
    SnapshotNotFoundError,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_add_bookmark_returns_list(isolated_stash):
    _save("snap1")
    result = add_bookmark("snap1")
    assert "snap1" in result


def test_add_bookmark_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        add_bookmark("ghost")


def test_add_duplicate_bookmark_raises(isolated_stash):
    _save("snap1")
    add_bookmark("snap1")
    with pytest.raises(BookmarkAlreadyExistsError):
        add_bookmark("snap1")


def test_remove_bookmark(isolated_stash):
    _save("snap1")
    add_bookmark("snap1")
    result = remove_bookmark("snap1")
    assert "snap1" not in result


def test_remove_missing_bookmark_raises(isolated_stash):
    with pytest.raises(BookmarkNotFoundError):
        remove_bookmark("nope")


def test_list_bookmarks_empty(isolated_stash):
    assert list_bookmarks() == []


def test_list_bookmarks_multiple(isolated_stash):
    _save("a")
    _save("b")
    add_bookmark("a")
    add_bookmark("b")
    result = list_bookmarks()
    assert result == ["a", "b"]


def test_is_bookmarked_true(isolated_stash):
    _save("snap1")
    add_bookmark("snap1")
    assert is_bookmarked("snap1") is True


def test_is_bookmarked_false(isolated_stash):
    assert is_bookmarked("snap1") is False


def test_remove_bookmark_does_not_affect_others(isolated_stash):
    """Removing one bookmark should leave other bookmarks intact."""
    _save("a")
    _save("b")
    add_bookmark("a")
    add_bookmark("b")
    remove_bookmark("a")
    assert is_bookmarked("b") is True
    assert is_bookmarked("a") is False
