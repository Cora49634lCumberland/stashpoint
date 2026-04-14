"""Tests for stashpoint.snapshot module."""

import os
import pytest

from stashpoint.snapshot import capture, drop, list_snapshots, restore, show


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    """Redirect stash storage to a temporary directory for each test."""
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))


def test_capture_all_env_vars(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    env_vars = capture("test")
    assert "MY_VAR" in env_vars
    assert env_vars["MY_VAR"] == "hello"


def test_capture_specific_keys(monkeypatch):
    monkeypatch.setenv("KEEP", "yes")
    monkeypatch.setenv("SKIP", "no")
    env_vars = capture("partial", keys=["KEEP"])
    assert "KEEP" in env_vars
    assert "SKIP" not in env_vars


def test_capture_ignores_missing_keys(monkeypatch):
    env_vars = capture("safe", keys=["DOES_NOT_EXIST_XYZ"])
    assert env_vars == {}


def test_restore_sets_env_vars(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    capture("mysnap")
    monkeypatch.delenv("FOO", raising=False)
    restore("mysnap")
    assert os.environ.get("FOO") == "bar"


def test_restore_raises_for_missing_snapshot():
    with pytest.raises(KeyError, match="ghost"):
        restore("ghost")


def test_restore_no_overwrite(monkeypatch):
    monkeypatch.setenv("VAR", "original")
    capture("snap")
    monkeypatch.setenv("VAR", "changed")
    restore("snap", overwrite=False)
    assert os.environ["VAR"] == "changed"


def test_drop_removes_snapshot(monkeypatch):
    monkeypatch.setenv("X", "1")
    capture("temp")
    assert drop("temp") is True
    assert "temp" not in list_snapshots()


def test_show_returns_snapshot_contents(monkeypatch):
    monkeypatch.setenv("SHOW_VAR", "visible")
    capture("visible_snap", keys=["SHOW_VAR"])
    contents = show("visible_snap")
    assert contents == {"SHOW_VAR": "visible"}


def test_show_raises_for_missing_snapshot():
    with pytest.raises(KeyError):
        show("no_such_snap")


def test_list_snapshots(monkeypatch):
    monkeypatch.setenv("A", "1")
    capture("alpha")
    capture("beta")
    names = list_snapshots()
    assert "alpha" in names
    assert "beta" in names
