"""Tests for stashpoint.cli_alias."""

import pytest
from click.testing import CliRunner
from stashpoint import storage
from stashpoint.cli_alias import alias_cmd


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    import stashpoint.alias as alias_mod
    monkeypatch.setattr(alias_mod, "get_stash_path", lambda: tmp_path)
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name, data=None):
    storage.save_snapshot(name, data or {"K": "v"})


def test_alias_set_success(runner, isolated_stash):
    _make_snapshot("prod")
    result = runner.invoke(alias_cmd, ["set", "p", "prod"])
    assert result.exit_code == 0
    assert "saved" in result.output


def test_alias_set_missing_snapshot(runner, isolated_stash):
    result = runner.invoke(alias_cmd, ["set", "p", "ghost"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_alias_resolve_success(runner, isolated_stash):
    _make_snapshot("prod")
    runner.invoke(alias_cmd, ["set", "p", "prod"])
    result = runner.invoke(alias_cmd, ["resolve", "p"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_alias_resolve_missing(runner, isolated_stash):
    result = runner.invoke(alias_cmd, ["resolve", "nope"])
    assert result.exit_code == 1


def test_alias_remove_success(runner, isolated_stash):
    _make_snapshot("prod")
    runner.invoke(alias_cmd, ["set", "p", "prod"])
    result = runner.invoke(alias_cmd, ["remove", "p"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_alias_list_empty(runner, isolated_stash):
    result = runner.invoke(alias_cmd, ["list"])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_alias_list_shows_entries(runner, isolated_stash):
    _make_snapshot("prod")
    runner.invoke(alias_cmd, ["set", "p", "prod"])
    result = runner.invoke(alias_cmd, ["list"])
    assert "p -> prod" in result.output
