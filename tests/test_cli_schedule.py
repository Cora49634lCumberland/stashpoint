import pytest
from click.testing import CliRunner
from stashpoint.cli_schedule import schedule_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name):
    save_snapshot(name, {"KEY": "val"})


def test_schedule_set_success(isolated_stash, runner):
    _make_snapshot("dev")
    result = runner.invoke(schedule_cmd, ["set", "dev", "daily"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_schedule_set_missing_snapshot(isolated_stash, runner):
    result = runner.invoke(schedule_cmd, ["set", "ghost", "daily"])
    assert result.exit_code == 1


def test_schedule_get_not_set(isolated_stash, runner):
    result = runner.invoke(schedule_cmd, ["get", "dev"])
    assert "No schedule" in result.output


def test_schedule_get_set(isolated_stash, runner):
    _make_snapshot("dev")
    runner.invoke(schedule_cmd, ["set", "dev", "weekly"])
    result = runner.invoke(schedule_cmd, ["get", "dev"])
    assert "weekly" in result.output


def test_schedule_list_empty(isolated_stash, runner):
    result = runner.invoke(schedule_cmd, ["list"])
    assert "No schedules" in result.output


def test_schedule_remove_success(isolated_stash, runner):
    _make_snapshot("dev")
    runner.invoke(schedule_cmd, ["set", "dev", "hourly"])
    result = runner.invoke(schedule_cmd, ["remove", "dev"])
    assert result.exit_code == 0


def test_schedule_remove_missing(isolated_stash, runner):
    result = runner.invoke(schedule_cmd, ["remove", "nope"])
    assert result.exit_code == 1
