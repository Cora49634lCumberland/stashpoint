"""Tests for stashpoint.audit."""

from __future__ import annotations

import pytest

from stashpoint import audit
from stashpoint.storage import get_stash_path


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage._STASH_DIR", str(tmp_path))
    monkeypatch.setattr("stashpoint.audit._get_audit_path",
                        lambda: tmp_path / "audit.json")
    yield tmp_path


def test_record_action_returns_entry():
    entry = audit.record_action("save", "mysnap")
    assert entry["action"] == "save"
    assert entry["snapshot"] == "mysnap"
    assert "timestamp" in entry
    assert entry["detail"] is None


def test_record_action_with_detail():
    entry = audit.record_action("rename", "snap1", detail="renamed to snap2")
    assert entry["detail"] == "renamed to snap2"


def test_get_audit_log_empty_when_no_file():
    result = audit.get_audit_log()
    assert result == []


def test_get_audit_log_newest_first():
    audit.record_action("save", "a")
    audit.record_action("restore", "b")
    audit.record_action("drop", "c")
    log = audit.get_audit_log()
    assert log[0]["action"] == "drop"
    assert log[-1]["action"] == "save"


def test_filter_by_snapshot_name():
    audit.record_action("save", "alpha")
    audit.record_action("save", "beta")
    audit.record_action("restore", "alpha")
    log = audit.get_audit_log(snapshot_name="alpha")
    assert all(e["snapshot"] == "alpha" for e in log)
    assert len(log) == 2


def test_filter_by_action():
    audit.record_action("save", "x")
    audit.record_action("restore", "x")
    audit.record_action("save", "y")
    log = audit.get_audit_log(action="save")
    assert all(e["action"] == "save" for e in log)
    assert len(log) == 2


def test_limit_parameter():
    for i in range(10):
        audit.record_action("save", f"snap{i}")
    log = audit.get_audit_log(limit=3)
    assert len(log) == 3


def test_clear_audit_log_returns_count():
    audit.record_action("save", "a")
    audit.record_action("save", "b")
    count = audit.clear_audit_log()
    assert count == 2
    assert audit.get_audit_log() == []
