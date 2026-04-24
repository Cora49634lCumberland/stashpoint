"""Workflow: ordered sequences of snapshots to apply in steps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class WorkflowNotFoundError(Exception):
    pass


class WorkflowAlreadyExistsError(Exception):
    pass


def _get_workflows_path() -> Path:
    return get_stash_path() / "workflows.json"


def _load_workflows() -> dict[str, list[str]]:
    p = _get_workflows_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(data: dict[str, list[str]]) -> None:
    _get_workflows_path().write_text(json.dumps(data, indent=2))


def create_workflow(name: str, steps: list[str]) -> list[str]:
    """Create a named workflow from an ordered list of snapshot names."""
    for step in steps:
        if load_snapshot(step) is None:
            raise SnapshotNotFoundError(f"Snapshot '{step}' not found")
    workflows = _load_workflows()
    if name in workflows:
        raise WorkflowAlreadyExistsError(f"Workflow '{name}' already exists")
    workflows[name] = list(steps)
    _save_workflows(workflows)
    return workflows[name]


def delete_workflow(name: str) -> None:
    """Remove a workflow by name."""
    workflows = _load_workflows()
    if name not in workflows:
        raise WorkflowNotFoundError(f"Workflow '{name}' not found")
    del workflows[name]
    _save_workflows(workflows)


def get_workflow(name: str) -> list[str]:
    """Return the ordered steps of a workflow."""
    workflows = _load_workflows()
    if name not in workflows:
        raise WorkflowNotFoundError(f"Workflow '{name}' not found")
    return workflows[name]


def list_workflows() -> dict[str, list[str]]:
    """Return all workflows."""
    return _load_workflows()


def append_step(workflow_name: str, snapshot_name: str) -> list[str]:
    """Append a snapshot step to an existing workflow."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found")
    workflows = _load_workflows()
    if workflow_name not in workflows:
        raise WorkflowNotFoundError(f"Workflow '{workflow_name}' not found")
    workflows[workflow_name].append(snapshot_name)
    _save_workflows(workflows)
    return workflows[workflow_name]
