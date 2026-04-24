"""Tests for stashpoint.workflow."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.workflow import (
    SnapshotNotFoundError,
    WorkflowAlreadyExistsError,
    WorkflowNotFoundError,
    append_step,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name: str, data: dict) -> None:
    storage.save_snapshot(name, data)


def test_create_workflow_basic():
    _save("snap_a", {"K": "1"})
    _save("snap_b", {"K": "2"})
    steps = create_workflow("deploy", ["snap_a", "snap_b"])
    assert steps == ["snap_a", "snap_b"]


def test_create_workflow_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        create_workflow("bad", ["nonexistent"])


def test_create_workflow_duplicate_raises():
    _save("snap_a", {"K": "1"})
    create_workflow("w1", ["snap_a"])
    with pytest.raises(WorkflowAlreadyExistsError):
        create_workflow("w1", ["snap_a"])


def test_get_workflow_returns_steps():
    _save("snap_a", {"K": "1"})
    _save("snap_b", {"K": "2"})
    create_workflow("pipe", ["snap_a", "snap_b"])
    assert get_workflow("pipe") == ["snap_a", "snap_b"]


def test_get_workflow_missing_raises():
    with pytest.raises(WorkflowNotFoundError):
        get_workflow("ghost")


def test_delete_workflow_removes_entry():
    _save("snap_a", {"K": "1"})
    create_workflow("to_del", ["snap_a"])
    delete_workflow("to_del")
    assert "to_del" not in list_workflows()


def test_delete_workflow_missing_raises():
    with pytest.raises(WorkflowNotFoundError):
        delete_workflow("nope")


def test_list_workflows_empty():
    assert list_workflows() == {}


def test_list_workflows_multiple():
    _save("s1", {"A": "1"})
    _save("s2", {"B": "2"})
    create_workflow("w1", ["s1"])
    create_workflow("w2", ["s2", "s1"])
    wf = list_workflows()
    assert set(wf.keys()) == {"w1", "w2"}


def test_append_step_adds_to_end():
    _save("s1", {"A": "1"})
    _save("s2", {"B": "2"})
    create_workflow("chain", ["s1"])
    steps = append_step("chain", "s2")
    assert steps == ["s1", "s2"]


def test_append_step_missing_snapshot_raises():
    _save("s1", {"A": "1"})
    create_workflow("chain", ["s1"])
    with pytest.raises(SnapshotNotFoundError):
        append_step("chain", "ghost")


def test_append_step_missing_workflow_raises():
    _save("s1", {"A": "1"})
    with pytest.raises(WorkflowNotFoundError):
        append_step("no_workflow", "s1")
