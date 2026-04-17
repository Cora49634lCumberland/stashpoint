import pytest
from click.testing import CliRunner
from stashpoint.cli_favorite import favorite_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name, data=None):
    save_snapshot(name, data or {"KEY": "val"})


def test_favorite_add_success(runner, isolated_stash):
    _make_snapshot("dev")
    result = runner.invoke(favorite_cmd, ["add", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_favorite_add_missing_snapshot(runner, isolated_stash):
    result = runner.invoke(favorite_cmd, ["add", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_favorite_add_duplicate(runner, isolated_stash):
    _make_snapshot("dev")
    runner.invoke(favorite_cmd, ["add", "dev"])
    result = runner.invoke(favorite_cmd, ["add", "dev"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_favorite_remove_success(runner, isolated_stash):
    _make_snapshot("dev")
    runner.invoke(favorite_cmd, ["add", "dev"])
    result = runner.invoke(favorite_cmd, ["remove", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_favorite_list_empty(runner, isolated_stash):
    result = runner.invoke(favorite_cmd, ["list"])
    assert result.exit_code == 0
    assert "No favorites" in result.output


def test_favorite_check_is_favorite(runner, isolated_stash):
    _make_snapshot("dev")
    runner.invoke(favorite_cmd, ["add", "dev"])
    result = runner.invoke(favorite_cmd, ["check", "dev"])
    assert "is a favorite" in result.output


def test_favorite_check_not_favorite(runner, isolated_stash):
    result = runner.invoke(favorite_cmd, ["check", "dev"])
    assert "not a favorite" in result.output
