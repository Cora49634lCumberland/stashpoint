"""CLI integration tests for the compare command."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_compare import compare_cmd
from stashpoint import storage


@pytest.fixture()
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name, data):
    storage.save_snapshot(name, data)


def test_compare_run_success(isolated_stash, runner):
    _make_snapshot("dev", {"FOO": "1", "SHARED": "yes"})
    _make_snapshot("prod", {"BAR": "2", "SHARED": "yes"})
    result = runner.invoke(compare_cmd, ["run", "dev", "prod"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
    assert "SHARED" in result.output


def test_compare_run_missing_snapshot(isolated_stash, runner):
    _make_snapshot("real", {"K": "v"})
    result = runner.invoke(compare_cmd, ["run", "real", "ghost"])
    assert result.exit_code != 0


def test_compare_run_too_few_args(isolated_stash, runner):
    _make_snapshot("solo", {"K": "v"})
    result = runner.invoke(compare_cmd, ["run", "solo"])
    assert result.exit_code != 0


def test_compare_run_json_output(isolated_stash, runner):
    import json
    _make_snapshot("a", {"X": "1"})
    _make_snapshot("b", {"X": "2"})
    result = runner.invoke(compare_cmd, ["run", "--json", "a", "b"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "keys" in data
    assert "shared" in data
    assert "unique" in data


def test_compare_run_three_snapshots(isolated_stash, runner):
    _make_snapshot("x", {"A": "1", "C": "shared"})
    _make_snapshot("y", {"B": "2", "C": "shared"})
    _make_snapshot("z", {"D": "3", "C": "shared"})
    result = runner.invoke(compare_cmd, ["run", "x", "y", "z"])
    assert result.exit_code == 0
    assert "C" in result.output
