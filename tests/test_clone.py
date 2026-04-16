"""Tests for stashpoint.clone."""

import pytest
from click.testing import CliRunner

from stashpoint.cli_clone import clone_cmd
from stashpoint.clone import (
    SnapshotAlreadyExistsError,
    SnapshotNotFoundError,
    clone_snapshot,
)
from stashpoint.storage import load_snapshot, save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))


def _save(name, data):
    save_snapshot(name, data)


def test_clone_basic():
    _save("src", {"A": "1", "B": "2"})
    result = clone_snapshot("src", "dst")
    assert result == {"A": "1", "B": "2"}
    assert load_snapshot("dst") == {"A": "1", "B": "2"}


def test_clone_does_not_mutate_source():
    _save("src", {"X": "hello"})
    clone_snapshot("src", "dst")
    assert load_snapshot("src") == {"X": "hello"}


def test_clone_with_key_filter():
    _save("src", {"A": "1", "B": "2", "C": "3"})
    result = clone_snapshot("src", "dst", keys=["A", "C"])
    assert result == {"A": "1", "C": "3"}
    assert "B" not in load_snapshot("dst")


def test_clone_missing_source_raises():
    with pytest.raises(SnapshotNotFoundError):
        clone_snapshot("ghost", "dst")


def test_clone_to_existing_raises():
    _save("src", {"A": "1"})
    _save("dst", {"B": "2"})
    with pytest.raises(SnapshotAlreadyExistsError):
        clone_snapshot("src", "dst")


def test_clone_overwrite_allowed():
    _save("src", {"A": "new"})
    _save("dst", {"A": "old"})
    result = clone_snapshot("src", "dst", overwrite=True)
    assert result == {"A": "new"}


def test_clone_run_cli_success():
    _save("src", {"K": "v"})
    runner = CliRunner()
    result = runner.invoke(clone_cmd, ["run", "src", "dst"])
    assert result.exit_code == 0
    assert "Cloned 'src' -> 'dst'" in result.output


def test_clone_run_cli_missing_source():
    runner = CliRunner()
    result = runner.invoke(clone_cmd, ["run", "ghost", "dst"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_clone_run_cli_with_keys():
    _save("src", {"A": "1", "B": "2"})
    runner = CliRunner()
    result = runner.invoke(clone_cmd, ["run", "src", "dst", "-k", "A"])
    assert result.exit_code == 0
    assert load_snapshot("dst") == {"A": "1"}
