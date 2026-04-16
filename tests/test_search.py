import pytest
import os
from unittest.mock import patch
from stashpoint.search import search_by_key, search_by_value, search_snapshots, NoSnapshotsFoundError
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name, data):
    save_snapshot(name, data)


def test_search_by_key_match():
    _save("dev", {"DATABASE_URL": "postgres://", "PORT": "5432"})
    results = search_by_key("DATABASE*")
    assert "dev" in results
    assert "DATABASE_URL" in results["dev"]
    assert "PORT" not in results["dev"]


def test_search_by_key_no_match():
    _save("dev", {"PORT": "5432"})
    results = search_by_key("DATABASE*")
    assert results == {}


def test_search_by_value_match():
    _save("prod", {"DB": "postgres://prod", "CACHE": "redis://"})
    results = search_by_value("postgres*")
    assert "prod" in results
    assert "DB" in results["prod"]
    assert "CACHE" not in results["prod"]


def test_search_by_value_no_match():
    _save("prod", {"DB": "mysql://"})
    results = search_by_value("postgres*")
    assert results == {}


def test_search_snapshots_combined():
    _save("staging", {"DB_URL": "postgres://staging", "DB_POOL": "10", "PORT": "8080"})
    results = search_snapshots(key_pattern="DB*", value_pattern="postgres*")
    assert "staging" in results
    assert "DB_URL" in results["staging"]
    assert "DB_POOL" not in results["staging"]


def test_search_snapshots_key_only():
    _save("local", {"SECRET_KEY": "abc", "PORT": "3000"})
    results = search_snapshots(key_pattern="SECRET*")
    assert "local" in results
    assert list(results["local"].keys()) == ["SECRET_KEY"]


def test_search_raises_when_no_snapshots():
    with pytest.raises(NoSnapshotsFoundError):
        search_snapshots(key_pattern="*")


def test_search_multiple_snapshots():
    _save("a", {"FOO": "bar"})
    _save("b", {"FOO": "baz", "OTHER": "x"})
    results = search_by_key("FOO")
    assert "a" in results
    assert "b" in results
