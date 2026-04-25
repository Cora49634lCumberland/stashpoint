"""Tests for stashpoint.trigger."""

from __future__ import annotations

import pytest

from stashpoint.trigger import (
    SnapshotNotFoundError,
    TriggerNotFoundError,
    list_triggers,
    remove_trigger,
    resolve_trigger,
    set_trigger,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.trigger.get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(tmp_path, name: str, data: dict) -> None:
    import json
    snapshots_file = tmp_path / "snapshots.json"
    existing = json.loads(snapshots_file.read_text()) if snapshots_file.exists() else {}
    existing[name] = data
    snapshots_file.write_text(json.dumps(existing))


def test_set_trigger_returns_snapshot_name(isolated_stash):
    _save(isolated_stash, "prod", {"ENV": "production"})
    result = set_trigger("on_deploy", "prod")
    assert result == "prod"


def test_set_trigger_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_trigger("on_deploy", "nonexistent")


def test_resolve_trigger_returns_snapshot_name(isolated_stash):
    _save(isolated_stash, "staging", {"ENV": "staging"})
    set_trigger("on_test", "staging")
    assert resolve_trigger("on_test") == "staging"


def test_resolve_trigger_returns_none_when_not_set(isolated_stash):
    assert resolve_trigger("unknown_trigger") is None


def test_set_trigger_overwrites_existing(isolated_stash):
    _save(isolated_stash, "prod", {"ENV": "production"})
    _save(isolated_stash, "staging", {"ENV": "staging"})
    set_trigger("on_deploy", "prod")
    set_trigger("on_deploy", "staging")
    assert resolve_trigger("on_deploy") == "staging"


def test_remove_trigger_removes_binding(isolated_stash):
    _save(isolated_stash, "prod", {"ENV": "production"})
    set_trigger("on_deploy", "prod")
    remove_trigger("on_deploy")
    assert resolve_trigger("on_deploy") is None


def test_remove_trigger_not_found_raises(isolated_stash):
    with pytest.raises(TriggerNotFoundError):
        remove_trigger("ghost_trigger")


def test_list_triggers_returns_all(isolated_stash):
    _save(isolated_stash, "prod", {"ENV": "production"})
    _save(isolated_stash, "dev", {"ENV": "development"})
    set_trigger("on_deploy", "prod")
    set_trigger("on_test", "dev")
    entries = list_triggers()
    triggers = {e["trigger"]: e["snapshot"] for e in entries}
    assert triggers["on_deploy"] == "prod"
    assert triggers["on_test"] == "dev"


def test_list_triggers_empty_when_none_set(isolated_stash):
    assert list_triggers() == []
