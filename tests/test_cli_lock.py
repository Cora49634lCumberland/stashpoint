"""CLI integration tests for lock commands."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_lock import lock_cmd
from stashpoint.lock import lock_snapshot
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str):
    save_snapshot(name, {"X": "1"})


def test_lock_add_success(runner, isolated_stash):
    _make_snapshot("prod")
    result = runner.invoke(lock_cmd, ["add", "prod"])
    assert result.exit_code == 0
    assert "locked" in result.output


def test_lock_add_missing_snapshot(runner, isolated_stash):
    result = runner.invoke(lock_cmd, ["add", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_lock_add_already_locked(runner, isolated_stash):
    _make_snapshot("prod")
    lock_snapshot("prod")
    result = runner.invoke(lock_cmd, ["add", "prod"])
    assert result.exit_code == 1
    assert "already locked" in result.output


def test_lock_remove_success(runner, isolated_stash):
    _make_snapshot("staging")
    lock_snapshot("staging")
    result = runner.invoke(lock_cmd, ["remove", "staging"])
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_lock_remove_not_locked(runner, isolated_stash):
    _make_snapshot("staging")
    result = runner.invoke(lock_cmd, ["remove", "staging"])
    assert result.exit_code == 1
    assert "not locked" in result.output


def test_lock_list_empty(runner, isolated_stash):
    result = runner.invoke(lock_cmd, ["list"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_lock_list_shows_locked(runner, isolated_stash):
    _make_snapshot("alpha")
    lock_snapshot("alpha")
    result = runner.invoke(lock_cmd, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output


def test_lock_check_locked(runner, isolated_stash):
    _make_snapshot("beta")
    lock_snapshot("beta")
    result = runner.invoke(lock_cmd, ["check", "beta"])
    assert result.exit_code == 0
    assert "is locked" in result.output


def test_lock_check_not_locked(runner, isolated_stash):
    _make_snapshot("beta")
    result = runner.invoke(lock_cmd, ["check", "beta"])
    assert result.exit_code == 0
    assert "not locked" in result.output
