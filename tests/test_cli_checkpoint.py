"""CLI tests for checkpoint commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashpoint.cli_checkpoint import checkpoint_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str) -> None:
    save_snapshot(name, {"K": "v"})


def test_checkpoint_add_success(runner):
    _make_snapshot("mysnap")
    result = runner.invoke(checkpoint_cmd, ["add", "mysnap", "v1"])
    assert result.exit_code == 0
    assert "v1" in result.output
    assert "mysnap" in result.output


def test_checkpoint_add_missing_snapshot(runner):
    result = runner.invoke(checkpoint_cmd, ["add", "ghost", "v1"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_checkpoint_add_duplicate(runner):
    _make_snapshot("mysnap")
    runner.invoke(checkpoint_cmd, ["add", "mysnap", "v1"])
    result = runner.invoke(checkpoint_cmd, ["add", "mysnap", "v1"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_checkpoint_list_shows_entries(runner):
    _make_snapshot("mysnap")
    runner.invoke(checkpoint_cmd, ["add", "mysnap", "alpha"])
    runner.invoke(checkpoint_cmd, ["add", "mysnap", "beta"])
    result = runner.invoke(checkpoint_cmd, ["list", "mysnap"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_checkpoint_list_empty(runner):
    _make_snapshot("mysnap")
    result = runner.invoke(checkpoint_cmd, ["list", "mysnap"])
    assert result.exit_code == 0
    assert "No checkpoints" in result.output


def test_checkpoint_remove_success(runner):
    _make_snapshot("mysnap")
    runner.invoke(checkpoint_cmd, ["add", "mysnap", "v1"])
    result = runner.invoke(checkpoint_cmd, ["remove", "mysnap", "v1"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_checkpoint_remove_missing(runner):
    _make_snapshot("mysnap")
    result = runner.invoke(checkpoint_cmd, ["remove", "mysnap", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output
