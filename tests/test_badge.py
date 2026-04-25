"""Tests for stashpoint.badge."""

from __future__ import annotations

import pytest

from stashpoint.badge import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    SnapshotNotFoundError,
    add_badge,
    find_by_badge,
    get_badges,
    remove_badge,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "val"})


def test_add_badge_returns_list(isolated_stash):
    _save("snap1")
    result = add_badge("snap1", "stable")
    assert result == ["stable"]


def test_add_multiple_badges(isolated_stash):
    _save("snap1")
    add_badge("snap1", "stable")
    result = add_badge("snap1", "prod")
    assert "stable" in result
    assert "prod" in result


def test_add_duplicate_badge_raises(isolated_stash):
    _save("snap1")
    add_badge("snap1", "wip")
    with pytest.raises(BadgeAlreadyExistsError):
        add_badge("snap1", "wip")


def test_add_badge_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        add_badge("ghost", "stable")


def test_remove_badge_returns_updated_list(isolated_stash):
    _save("snap1")
    add_badge("snap1", "stable")
    add_badge("snap1", "wip")
    result = remove_badge("snap1", "stable")
    assert "stable" not in result
    assert "wip" in result


def test_remove_badge_not_assigned_raises(isolated_stash):
    _save("snap1")
    with pytest.raises(BadgeNotFoundError):
        remove_badge("snap1", "stable")


def test_remove_badge_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        remove_badge("ghost", "stable")


def test_get_badges_returns_empty_when_none(isolated_stash):
    _save("snap1")
    assert get_badges("snap1") == []


def test_get_badges_returns_stored(isolated_stash):
    _save("snap1")
    add_badge("snap1", "experimental")
    assert get_badges("snap1") == ["experimental"]


def test_find_by_badge_returns_matching_snapshots(isolated_stash):
    _save("snap1")
    _save("snap2")
    _save("snap3")
    add_badge("snap1", "prod")
    add_badge("snap3", "prod")
    add_badge("snap2", "dev")
    result = find_by_badge("prod")
    assert set(result) == {"snap1", "snap3"}


def test_find_by_badge_returns_empty_when_none(isolated_stash):
    _save("snap1")
    assert find_by_badge("stable") == []
