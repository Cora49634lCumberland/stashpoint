"""Tests for stashpoint.cli_namespace."""

import pytest
from click.testing import CliRunner
from stashpoint.cli_namespace import namespace_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.namespace.get_stash_path", lambda: tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name, data=None):
    save_snapshot(name, data or {"KEY": "value"})


def test_namespace_create_success(runner):
    result = runner.invoke(namespace_cmd, ["create", "prod"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_namespace_create_duplicate(runner):
    runner.invoke(namespace_cmd, ["create", "prod"])
    result = runner.invoke(namespace_cmd, ["create", "prod"])
    assert result.exit_code == 1


def test_namespace_delete_success(runner):
    runner.invoke(namespace_cmd, ["create", "staging"])
    result = runner.invoke(namespace_cmd, ["delete", "staging"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_namespace_delete_missing(runner):
    result = runner.invoke(namespace_cmd, ["delete", "ghost"])
    assert result.exit_code == 1


def test_namespace_add_success(runner):
    _make_snapshot("snap1")
    runner.invoke(namespace_cmd, ["create", "dev"])
    result = runner.invoke(namespace_cmd, ["add", "dev", "snap1"])
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_namespace_add_missing_snapshot(runner):
    runner.invoke(namespace_cmd, ["create", "dev"])
    result = runner.invoke(namespace_cmd, ["add", "dev", "ghost"])
    assert result.exit_code == 1


def test_namespace_list_empty(runner):
    result = runner.invoke(namespace_cmd, ["list"])
    assert result.exit_code == 0
    assert "No namespaces" in result.output


def test_namespace_list_with_entries(runner):
    runner.invoke(namespace_cmd, ["create", "alpha"])
    result = runner.invoke(namespace_cmd, ["list"])
    assert "alpha" in result.output
