"""Tests for stashpoint.copy."""

import os
import pytest

from stashpoint.copy import (
    SnapshotAlreadyExistsError,
    SnapshotNotFoundError,
    copy_snapshot,
)
from stashpoint.storage import load_snapshot, save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict) -> None:
    save_snapshot(name, data)


def test_copy_basic():
    _save("original", {"FOO": "bar", "BAZ": "qux"})
    result = copy_snapshot("original", "clone")
    assert result == {"FOO": "bar", "BAZ": "qux"}
    assert load_snapshot("clone") == {"FOO": "bar", "BAZ": "qux"}


def test_copy_does_not_mutate_source():
    _save("src", {"KEY": "value"})
    copy_snapshot("src", "dst")
    assert load_snapshot("src") == {"KEY": "value"}


def test_copy_missing_source_raises():
    with pytest.raises(SnapshotNotFoundError, match="'missing'"):
        copy_snapshot("missing", "anywhere")


def test_copy_existing_destination_raises_without_overwrite():
    _save("a", {"X": "1"})
    _save("b", {"X": "2"})
    with pytest.raises(SnapshotAlreadyExistsError, match="'b'"):
        copy_snapshot("a", "b")


def test_copy_existing_destination_with_overwrite():
    _save("a", {"X": "1"})
    _save("b", {"X": "2"})
    result = copy_snapshot("a", "b", overwrite=True)
    assert result == {"X": "1"}
    assert load_snapshot("b") == {"X": "1"}


def test_copy_returns_copied_data():
    payload = {"ALPHA": "a", "BETA": "b", "GAMMA": "c"}
    _save("snap", payload)
    returned = copy_snapshot("snap", "snap_copy")
    assert returned == payload


def test_copy_creates_independent_snapshot():
    """Modifying the original after copy should not affect the copy."""
    _save("original", {"ENV": "prod"})
    copy_snapshot("original", "backup")
    # Overwrite the original
    _save("original", {"ENV": "staging"})
    assert load_snapshot("backup") == {"ENV": "prod"}
