"""CLI tests for the copy command."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_copy import copy_cmd
from stashpoint.storage import load_snapshot, save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def _make_snapshot(name: str, data: dict | None = None) -> None:
    save_snapshot(name, data or {"KEY": "val"})


def test_copy_run_success(runner):
    _make_snapshot("src", {"A": "1"})
    result = runner.invoke(copy_cmd, ["run", "src", "dst"])
    assert result.exit_code == 0
    assert "copied" in result.output
    assert load_snapshot("dst") == {"A": "1"}


def test_copy_run_missing_source(runner):
    result = runner.invoke(copy_cmd, ["run", "ghost", "dst"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_copy_run_destination_exists_no_overwrite(runner):
    _make_snapshot("src", {"A": "1"})
    _make_snapshot("dst", {"B": "2"})
    result = runner.invoke(copy_cmd, ["run", "src", "dst"])
    assert result.exit_code == 1
    assert "Error" in result.output
    # dst should remain unchanged
    assert load_snapshot("dst") == {"B": "2"}


def test_copy_run_destination_exists_with_overwrite(runner):
    _make_snapshot("src", {"A": "1"})
    _make_snapshot("dst", {"B": "2"})
    result = runner.invoke(copy_cmd, ["run", "src", "dst", "--overwrite"])
    assert result.exit_code == 0
    assert load_snapshot("dst") == {"A": "1"}


def test_copy_run_output_message(runner):
    _make_snapshot("alpha", {"Z": "99"})
    result = runner.invoke(copy_cmd, ["run", "alpha", "beta"])
    assert "alpha" in result.output
    assert "beta" in result.output
