"""Tests for stashpoint.alias."""

import pytest
from stashpoint import storage
from stashpoint.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    SnapshotNotFoundError,
    AliasNotFoundError,
)


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_path", lambda: tmp_path)
    import stashpoint.alias as alias_mod
    monkeypatch.setattr(alias_mod, "get_stash_path", lambda: tmp_path)
    yield tmp_path


def _save(name, data):
    storage.save_snapshot(name, data)


def test_set_alias_returns_alias(isolated_stash):
    _save("prod", {"KEY": "val"})
    result = set_alias("p", "prod")
    assert result == "p"


def test_resolve_alias_returns_snapshot_name(isolated_stash):
    _save("prod", {"KEY": "val"})
    set_alias("p", "prod")
    assert resolve_alias("p") == "prod"


def test_set_alias_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_alias("x", "nonexistent")


def test_remove_alias(isolated_stash):
    _save("prod", {"KEY": "val"})
    set_alias("p", "prod")
    remove_alias("p")
    with pytest.raises(AliasNotFoundError):
        resolve_alias("p")


def test_remove_missing_alias_raises(isolated_stash):
    with pytest.raises(AliasNotFoundError):
        remove_alias("ghost")


def test_list_aliases_empty(isolated_stash):
    assert list_aliases() == {}


def test_list_aliases_multiple(isolated_stash):
    _save("prod", {"A": "1"})
    _save("dev", {"B": "2"})
    set_alias("p", "prod")
    set_alias("d", "dev")
    aliases = list_aliases()
    assert aliases == {"p": "prod", "d": "dev"}


def test_overwrite_alias(isolated_stash):
    _save("prod", {"A": "1"})
    _save("dev", {"B": "2"})
    set_alias("env", "prod")
    set_alias("env", "dev")
    assert resolve_alias("env") == "dev"
