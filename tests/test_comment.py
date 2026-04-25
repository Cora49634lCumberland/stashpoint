"""Tests for stashpoint.comment."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.comment import (
    SnapshotNotFoundError,
    get_comment,
    list_comments,
    remove_comment,
    set_comment,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    import stashpoint.comment as comment_mod
    monkeypatch.setattr(comment_mod, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    storage.save_snapshot(name, data or {"KEY": "val"})


# ---------------------------------------------------------------------------
# set_comment
# ---------------------------------------------------------------------------

def test_set_comment_returns_text(isolated_stash):
    _save("snap1")
    result = set_comment("snap1", "pre-deploy build")
    assert result == "pre-deploy build"


def test_set_comment_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_comment("ghost", "some comment")


def test_set_comment_overwrites_previous(isolated_stash):
    _save("snap1")
    set_comment("snap1", "first")
    set_comment("snap1", "second")
    assert get_comment("snap1") == "second"


# ---------------------------------------------------------------------------
# get_comment
# ---------------------------------------------------------------------------

def test_get_comment_returns_stored_text(isolated_stash):
    _save("snap1")
    set_comment("snap1", "hello world")
    assert get_comment("snap1") == "hello world"


def test_get_comment_returns_none_when_not_set(isolated_stash):
    _save("snap1")
    assert get_comment("snap1") is None


# ---------------------------------------------------------------------------
# remove_comment
# ---------------------------------------------------------------------------

def test_remove_comment_clears_entry(isolated_stash):
    _save("snap1")
    set_comment("snap1", "temporary")
    remove_comment("snap1")
    assert get_comment("snap1") is None


def test_remove_comment_noop_when_not_set(isolated_stash):
    _save("snap1")
    remove_comment("snap1")  # should not raise
    assert get_comment("snap1") is None


# ---------------------------------------------------------------------------
# list_comments
# ---------------------------------------------------------------------------

def test_list_comments_returns_all(isolated_stash):
    _save("a")
    _save("b")
    set_comment("a", "comment-a")
    set_comment("b", "comment-b")
    result = list_comments()
    assert result == {"a": "comment-a", "b": "comment-b"}


def test_list_comments_empty_when_none_set(isolated_stash):
    assert list_comments() == {}
