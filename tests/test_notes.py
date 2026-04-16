"""Tests for stashpoint.notes."""

from __future__ import annotations

import pytest

from stashpoint.notes import (
    SnapshotNotFoundError,
    get_note,
    list_notes,
    remove_note,
    set_note,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None):
    save_snapshot(name, data or {"KEY": "val"})


def test_set_note_returns_text():
    _save("snap1")
    result = set_note("snap1", "my note")
    assert result == "my note"


def test_get_note_returns_stored_text():
    _save("snap1")
    set_note("snap1", "hello world")
    assert get_note("snap1") == "hello world"


def test_get_note_returns_none_when_not_set():
    _save("snap1")
    assert get_note("snap1") is None


def test_set_note_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_note("ghost", "nope")


def test_set_note_overwrites_existing():
    _save("snap1")
    set_note("snap1", "first")
    set_note("snap1", "second")
    assert get_note("snap1") == "second"


def test_remove_note_clears_entry():
    _save("snap1")
    set_note("snap1", "to remove")
    remove_note("snap1")
    assert get_note("snap1") is None


def test_remove_note_no_op_when_not_set():
    _save("snap1")
    remove_note("snap1")  # should not raise


def test_list_notes_returns_all():
    _save("a")
    _save("b")
    set_note("a", "note a")
    set_note("b", "note b")
    notes = list_notes()
    assert notes == {"a": "note a", "b": "note b"}


def test_list_notes_empty_when_none_set():
    assert list_notes() == {}
