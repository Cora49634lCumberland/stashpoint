"""Tests for stashpoint.rename."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from stashpoint.rename import (
    rename_snapshot,
    SnapshotNotFoundError,
    SnapshotAlreadyExistsError,
)
from stashpoint.storage import save_snapshot, load_snapshot, load_snapshots


@pytest.fixture
def isolated_stash(tmp_path):
    with patch("stashpoint.storage.get_stash_path", return_value=tmp_path), \
         patch("stashpoint.rename.get_stash_path", return_value=tmp_path):
        yield tmp_path


def _save(name, data, stash_path):
    save_snapshot(name, data, stash_path)


def test_rename_basic(isolated_stash):
    _save("alpha", {"KEY": "val"}, isolated_stash)
    rename_snapshot("alpha", "beta", stash_path=isolated_stash)

    assert load_snapshot("beta", isolated_stash) == {"KEY": "val"}
    assert load_snapshot("alpha", isolated_stash) is None


def test_rename_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        rename_snapshot("ghost", "new_name", stash_path=isolated_stash)


def test_rename_to_existing_name_raises(isolated_stash):
    _save("alpha", {"A": "1"}, isolated_stash)
    _save("beta", {"B": "2"}, isolated_stash)

    with pytest.raises(SnapshotAlreadyExistsError):
        rename_snapshot("alpha", "beta", stash_path=isolated_stash)


def test_rename_updates_tags(isolated_stash):
    _save("alpha", {"X": "1"}, isolated_stash)
    tags_file = isolated_stash / "tags.json"
    tags_file.write_text(json.dumps({"alpha": ["prod", "stable"]}))

    rename_snapshot("alpha", "gamma", stash_path=isolated_stash)

    data = json.loads(tags_file.read_text())
    assert "gamma" in data
    assert data["gamma"] == ["prod", "stable"]
    assert "alpha" not in data


def test_rename_updates_pins(isolated_stash):
    _save("alpha", {"X": "1"}, isolated_stash)
    pins_file = isolated_stash / "pins.json"
    pins_file.write_text(json.dumps({"alpha": True}))

    rename_snapshot("alpha", "delta", stash_path=isolated_stash)

    data = json.loads(pins_file.read_text())
    assert "delta" in data
    assert "alpha" not in data


def test_rename_skips_missing_metadata_files(isolated_stash):
    _save("alpha", {"X": "1"}, isolated_stash)
    # No tags.json, pins.json, or locks.json present — should not raise
    rename_snapshot("alpha", "omega", stash_path=isolated_stash)
    assert load_snapshot("omega", isolated_stash) == {"X": "1"}


def test_rename_preserves_other_snapshots(isolated_stash):
    _save("alpha", {"A": "1"}, isolated_stash)
    _save("other", {"O": "2"}, isolated_stash)

    rename_snapshot("alpha", "renamed", stash_path=isolated_stash)

    snapshots = load_snapshots(isolated_stash)
    assert "other" in snapshots
    assert "renamed" in snapshots
    assert "alpha" not in snapshots
