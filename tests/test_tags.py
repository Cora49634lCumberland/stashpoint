"""Tests for stashpoint.tags."""

from __future__ import annotations

import os
import pytest

from stashpoint.tags import (
    SnapshotNotFoundError,
    add_tag,
    get_tags,
    list_by_tag,
    remove_tag,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _make_snapshot(name: str) -> None:
    save_snapshot(name, {"KEY": "value"})


def test_add_tag_returns_tag_list():
    _make_snapshot("snap1")
    result = add_tag("snap1", "production")
    assert "production" in result


def test_add_duplicate_tag_is_idempotent():
    _make_snapshot("snap1")
    add_tag("snap1", "production")
    result = add_tag("snap1", "production")
    assert result.count("production") == 1


def test_add_multiple_tags():
    _make_snapshot("snap1")
    add_tag("snap1", "production")
    add_tag("snap1", "backend")
    tags = get_tags("snap1")
    assert set(tags) == {"production", "backend"}


def test_remove_tag():
    _make_snapshot("snap1")
    add_tag("snap1", "production")
    result = remove_tag("snap1", "production")
    assert "production" not in result


def test_remove_nonexistent_tag_is_safe():
    _make_snapshot("snap1")
    result = remove_tag("snap1", "ghost")
    assert result == []


def test_get_tags_empty_for_untagged_snapshot():
    _make_snapshot("snap1")
    assert get_tags("snap1") == []


def test_list_by_tag_returns_matching_snapshots():
    _make_snapshot("snap1")
    _make_snapshot("snap2")
    _make_snapshot("snap3")
    add_tag("snap1", "production")
    add_tag("snap3", "production")
    add_tag("snap2", "staging")
    result = list_by_tag("production")
    assert set(result) == {"snap1", "snap3"}


def test_list_by_tag_empty_when_no_match():
    _make_snapshot("snap1")
    assert list_by_tag("nonexistent") == []


def test_tags_persist_across_calls():
    _make_snapshot("snap1")
    add_tag("snap1", "ci")
    # Reload from disk by calling get_tags in a fresh call
    assert "ci" in get_tags("snap1")
