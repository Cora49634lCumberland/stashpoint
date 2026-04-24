"""CLI tests for workflow commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashpoint import storage
from stashpoint.cli_workflow import workflow_cmd


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str, data: dict | None = None) -> None:
    storage.save_snapshot(name, data or {"KEY": "val"})


def test_workflow_create_success(runner):
    _make_snapshot("s1")
    _make_snapshot("s2")
    result = runner.invoke(workflow_cmd, ["create", "deploy", "s1", "s2"])
    assert result.exit_code == 0
    assert "deploy" in result.output


def test_workflow_create_missing_snapshot(runner):
    result = runner.invoke(workflow_cmd, ["create", "bad", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_workflow_list_empty(runner):
    result = runner.invoke(workflow_cmd, ["list"])
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_workflow_show_success(runner):
    _make_snapshot("s1")
    runner.invoke(workflow_cmd, ["create", "mywf", "s1"])
    result = runner.invoke(workflow_cmd, ["show", "mywf"])
    assert result.exit_code == 0
    assert "s1" in result.output


def test_workflow_show_missing(runner):
    result = runner.invoke(workflow_cmd, ["show", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_workflow_delete_success(runner):
    _make_snapshot("s1")
    runner.invoke(workflow_cmd, ["create", "to_del", "s1"])
    result = runner.invoke(workflow_cmd, ["delete", "to_del"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_workflow_append_success(runner):
    _make_snapshot("s1")
    _make_snapshot("s2")
    runner.invoke(workflow_cmd, ["create", "chain", "s1"])
    result = runner.invoke(workflow_cmd, ["append", "chain", "s2"])
    assert result.exit_code == 0
    assert "2 step" in result.output
