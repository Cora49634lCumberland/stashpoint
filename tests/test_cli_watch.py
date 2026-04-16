"""Tests for CLI watch commands."""

import pytest
from click.testing import CliRunner
from stashpoint.cli_watch import watch_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name, data):
    save_snapshot(name, data)


def test_watch_check_no_drift(runner, monkeypatch):
    _make_snapshot("snap", {"MY_VAR": "hello"})
    monkeypatch.setenv("MY_VAR", "hello")
    result = runner.invoke(watch_cmd, ["check", "snap"])
    assert result.exit_code == 0
    assert "No drift" in result.output


def test_watch_check_drift_found(runner, monkeypatch):
    _make_snapshot("snap", {"MY_VAR": "hello"})
    monkeypatch.setenv("MY_VAR", "world")
    result = runner.invoke(watch_cmd, ["check", "snap"])
    assert result.exit_code == 1
    assert "MY_VAR" in result.output


def test_watch_check_missing_snapshot(runner):
    result = runner.invoke(watch_cmd, ["check", "ghost"])
    assert result.exit_code == 2


def test_watch_check_quiet_no_drift(runner, monkeypatch):
    _make_snapshot("snap", {"K": "v"})
    monkeypatch.setenv("K", "v")
    result = runner.invoke(watch_cmd, ["check", "snap", "--quiet"])
    assert result.exit_code == 0
    assert result.output == ""


def test_watch_check_quiet_drift(runner, monkeypatch):
    _make_snapshot("snap", {"K": "v"})
    monkeypatch.setenv("K", "different")
    result = runner.invoke(watch_cmd, ["check", "snap", "--quiet"])
    assert result.exit_code == 1
    assert result.output == ""
