import pytest
from click.testing import CliRunner
from stashpoint.cli_archive import archive_cmd
from stashpoint.storage import save_snapshot
from stashpoint.archive import archive_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name, data=None):
    save_snapshot(name, data or {"K": "v"})


def test_archive_add_success(runner, isolated_stash):
    _make_snapshot("dev")
    result = runner.invoke(archive_cmd, ["add", "dev"])
    assert result.exit_code == 0
    assert "archived" in result.output


def test_archive_add_missing_snapshot(runner, isolated_stash):
    result = runner.invoke(archive_cmd, ["add", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_archive_list_shows_archived(runner, isolated_stash):
    _make_snapshot("dev")
    archive_snapshot("dev")
    result = runner.invoke(archive_cmd, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_archive_list_empty(runner, isolated_stash):
    result = runner.invoke(archive_cmd, ["list"])
    assert result.exit_code == 0
    assert "No archived" in result.output


def test_archive_restore_success(runner, isolated_stash):
    _make_snapshot("dev")
    archive_snapshot("dev")
    result = runner.invoke(archive_cmd, ["restore", "dev"])
    assert result.exit_code == 0
    assert "restored" in result.output


def test_archive_restore_not_archived(runner, isolated_stash):
    result = runner.invoke(archive_cmd, ["restore", "ghost"])
    assert result.exit_code == 1
    assert "Error" in result.output
