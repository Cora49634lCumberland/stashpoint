"""CLI tests for dependency commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashpoint import storage
from stashpoint.cli_dependency import dependency_cmd


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str) -> None:
    storage.save_snapshot(name, {"KEY": "value"})


def test_dependency_add_success(runner):
    _make_snapshot("a")
    _make_snapshot("b")
    result = runner.invoke(dependency_cmd, ["add", "a", "b"])
    assert result.exit_code == 0
    assert "Added dependency: a -> b" in result.output


def test_dependency_add_missing_snapshot(runner):
    _make_snapshot("a")
    result = runner.invoke(dependency_cmd, ["add", "a", "ghost"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_dependency_add_circular(runner):
    _make_snapshot("a")
    _make_snapshot("b")
    runner.invoke(dependency_cmd, ["add", "a", "b"])
    result = runner.invoke(dependency_cmd, ["add", "b", "a"])
    assert result.exit_code == 1
    assert "cycle" in result.output


def test_dependency_list_success(runner):
    _make_snapshot("a")
    _make_snapshot("b")
    runner.invoke(dependency_cmd, ["add", "a", "b"])
    result = runner.invoke(dependency_cmd, ["list", "a"])
    assert result.exit_code == 0
    assert "b" in result.output


def test_dependency_list_empty(runner):
    _make_snapshot("a")
    result = runner.invoke(dependency_cmd, ["list", "a"])
    assert result.exit_code == 0
    assert "no dependencies" in result.output


def test_dependency_remove_success(runner):
    _make_snapshot("a")
    _make_snapshot("b")
    runner.invoke(dependency_cmd, ["add", "a", "b"])
    result = runner.invoke(dependency_cmd, ["remove", "a", "b"])
    assert result.exit_code == 0
    assert "Removed dependency" in result.output


def test_dependency_dependents_success(runner):
    _make_snapshot("a")
    _make_snapshot("b")
    runner.invoke(dependency_cmd, ["add", "b", "a"])
    result = runner.invoke(dependency_cmd, ["dependents", "a"])
    assert result.exit_code == 0
    assert "b" in result.output
