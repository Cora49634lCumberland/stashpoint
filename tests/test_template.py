"""Tests for stashpoint.template."""

from __future__ import annotations

import pytest

from stashpoint import storage
from stashpoint.template import (
    SnapshotNotFoundError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
    delete_template,
    instantiate_template,
    list_templates,
    save_as_template,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    stash_file = tmp_path / "stash.json"
    monkeypatch.setattr(storage, "get_stash_path", lambda: stash_file)
    # also redirect templates file via same tmp_path
    import stashpoint.template as tpl_mod
    monkeypatch.setattr(tpl_mod, "get_stash_path", lambda: stash_file)
    yield tmp_path


def _save(name: str, data: dict) -> None:
    storage.save_snapshot(name, data)


def test_save_as_template_creates_entry():
    _save("dev", {"DEBUG": "1", "PORT": "8000"})
    save_as_template("dev", "base-dev")
    assert "base-dev" in list_templates()


def test_save_as_template_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        save_as_template("nonexistent", "tmpl")


def test_save_as_template_duplicate_raises():
    _save("dev", {"A": "1"})
    save_as_template("dev", "tmpl")
    with pytest.raises(TemplateAlreadyExistsError):
        save_as_template("dev", "tmpl")


def test_instantiate_template_creates_snapshot():
    _save("dev", {"KEY": "val"})
    save_as_template("dev", "tmpl")
    data = instantiate_template("tmpl", "new-snap")
    loaded = storage.load_snapshot("new-snap")
    assert loaded == {"KEY": "val"}
    assert data == {"KEY": "val"}


def test_instantiate_template_missing_raises():
    with pytest.raises(TemplateNotFoundError):
        instantiate_template("ghost", "snap")


def test_instantiate_does_not_mutate_template():
    _save("dev", {"X": "1"})
    save_as_template("dev", "tmpl")
    instantiate_template("tmpl", "snap1")
    # Modify the new snapshot directly via storage
    storage.save_snapshot("snap1", {"X": "changed"})
    # Template data should be unchanged
    data = instantiate_template("tmpl", "snap2")
    assert data["X"] == "1"


def test_list_templates_sorted():
    for name in ["zebra", "alpha", "middle"]:
        _save(name, {"K": name})
        save_as_template(name, name)
    assert list_templates() == ["alpha", "middle", "zebra"]


def test_list_templates_empty():
    assert list_templates() == []


def test_delete_template_removes_entry():
    _save("dev", {"A": "1"})
    save_as_template("dev", "tmpl")
    delete_template("tmpl")
    assert "tmpl" not in list_templates()


def test_delete_missing_template_raises():
    with pytest.raises(TemplateNotFoundError):
        delete_template("nope")
