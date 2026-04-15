"""Tests for stashpoint.history module."""

import os
import pytest

from stashpoint import history as hist


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def test_record_and_get_history():
    hist.record_event("save", "myenv")
    entries = hist.get_history()
    assert len(entries) == 1
    assert entries[0]["action"] == "save"
    assert entries[0]["snapshot"] == "myenv"
    assert "timestamp" in entries[0]


def test_multiple_events_are_ordered_most_recent_first():
    hist.record_event("save", "alpha")
    hist.record_event("restore", "alpha")
    hist.record_event("drop", "alpha")
    entries = hist.get_history(snapshot_name="alpha")
    assert entries[0]["action"] == "drop"
    assert entries[1]["action"] == "restore"
    assert entries[2]["action"] == "save"


def test_filter_by_snapshot_name():
    hist.record_event("save", "proj-a")
    hist.record_event("save", "proj-b")
    hist.record_event("restore", "proj-a")
    entries = hist.get_history(snapshot_name="proj-a")
    assert all(e["snapshot"] == "proj-a" for e in entries)
    assert len(entries) == 2


def test_limit_parameter():
    for i in range(10):
        hist.record_event("save", f"snap-{i}")
    entries = hist.get_history(limit=3)
    assert len(entries) == 3


def test_meta_is_stored():
    hist.record_event("merge", "merged", meta={"sources": ["a", "b"]})
    entries = hist.get_history(snapshot_name="merged")
    assert entries[0]["meta"] == {"sources": ["a", "b"]}


def test_clear_all_history():
    hist.record_event("save", "x")
    hist.record_event("save", "y")
    removed = hist.clear_history()
    assert removed == 2
    assert hist.get_history() == []


def test_clear_history_for_specific_snapshot():
    hist.record_event("save", "keep")
    hist.record_event("save", "remove")
    hist.record_event("restore", "remove")
    removed = hist.clear_history(snapshot_name="remove")
    assert removed == 2
    remaining = hist.get_history()
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "keep"


def test_empty_history_returns_empty_list():
    assert hist.get_history() == []


def test_history_persists_across_calls():
    hist.record_event("save", "persist")
    hist.record_event("restore", "persist")
    # Reload by calling get_history fresh
    entries = hist.get_history(snapshot_name="persist")
    assert len(entries) == 2


def test_limit_zero_returns_empty_list():
    """A limit of 0 should return an empty list, not all entries."""
    hist.record_event("save", "snap-a")
    hist.record_event("save", "snap-b")
    entries = hist.get_history(limit=0)
    assert entries == []


def test_limit_exceeding_total_returns_all():
    """A limit larger than the total number of entries should return all entries."""
    hist.record_event("save", "snap-a")
    hist.record_event("restore", "snap-a")
    entries = hist.get_history(limit=100)
    assert len(entries) == 2
