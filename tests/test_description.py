"""Tests for stashpoint.description module."""

from __future__ import annotations

import pytest

from stashpoint.description import (
    SnapshotNotFoundError,
    get_description,
    list_descriptions,
    remove_description,
    set_description,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


def _save(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "value"})


def test_set_description_returns_text():
    _save("snap1")
    result = set_description("snap1", "My first snapshot")
    assert result == "My first snapshot"


def test_get_description_returns_stored_text():
    _save("snap1")
    set_description("snap1", "Staging environment")
    assert get_description("snap1") == "Staging environment"


def test_get_description_returns_none_when_not_set():
    _save("snap1")
    assert get_description("snap1") is None


def test_set_description_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_description("ghost", "should fail")


def test_set_description_overwrites_existing():
    _save("snap1")
    set_description("snap1", "original")
    set_description("snap1", "updated")
    assert get_description("snap1") == "updated"


def test_remove_description_clears_entry():
    _save("snap1")
    set_description("snap1", "to be removed")
    remove_description("snap1")
    assert get_description("snap1") is None


def test_remove_description_is_noop_when_not_set():
    _save("snap1")
    # Should not raise
    remove_description("snap1")


def test_list_descriptions_returns_all():
    _save("snap1")
    _save("snap2")
    set_description("snap1", "first")
    set_description("snap2", "second")
    result = list_descriptions()
    assert result == {"snap1": "first", "snap2": "second"}


def test_list_descriptions_empty_when_none_set():
    assert list_descriptions() == {}
