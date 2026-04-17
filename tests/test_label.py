"""Tests for stashpoint.label."""

import pytest
from stashpoint import label as label_mod
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr("stashpoint.storage.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.label.get_stash_path", lambda: tmp_path)
    monkeypatch.setattr("stashpoint.label.load_snapshot",
                        lambda name: _snapshots.get(name))
    _snapshots.clear()
    _snapshots["dev"] = {"APP_ENV": "development"}
    yield


_snapshots: dict = {}


def _save(name, data):
    _snapshots[name] = data


def test_set_label_returns_label():
    result = label_mod.set_label("dev", "my-dev")
    assert result == "my-dev"


def test_set_label_missing_snapshot_raises():
    with pytest.raises(label_mod.SnapshotNotFoundError):
        label_mod.set_label("nonexistent", "oops")


def test_resolve_label_returns_snapshot_name(tmp_path):
    label_mod.set_label("dev", "my-dev")
    assert label_mod.resolve_label("my-dev") == "dev"


def test_resolve_missing_label_raises():
    with pytest.raises(label_mod.LabelNotFoundError):
        label_mod.resolve_label("ghost")


def test_remove_label(tmp_path):
    label_mod.set_label("dev", "my-dev")
    label_mod.remove_label("my-dev")
    with pytest.raises(label_mod.LabelNotFoundError):
        label_mod.resolve_label("my-dev")


def test_remove_missing_label_raises():
    with pytest.raises(label_mod.LabelNotFoundError):
        label_mod.remove_label("ghost")


def test_list_labels_empty(tmp_path):
    assert label_mod.list_labels() == {}


def test_list_labels_returns_all(tmp_path):
    _save("prod", {"APP_ENV": "production"})
    label_mod.set_label("dev", "lbl-dev")
    label_mod.set_label("prod", "lbl-prod")
    labels = label_mod.list_labels()
    assert labels["lbl-dev"] == "dev"
    assert labels["lbl-prod"] == "prod"


def test_set_label_overwrites_existing(tmp_path):
    _save("staging", {"APP_ENV": "staging"})
    label_mod.set_label("dev", "shared-label")
    label_mod.set_label("staging", "shared-label")
    assert label_mod.resolve_label("shared-label") == "staging"
