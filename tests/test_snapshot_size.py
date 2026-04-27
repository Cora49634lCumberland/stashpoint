"""Tests for stashpoint.snapshot_size."""

from __future__ import annotations

import pytest

from stashpoint.snapshot_size import (
    SnapshotNotFoundError,
    compute_size,
    get_size,
    list_sizes,
    remove_size,
)
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict) -> None:
    save_snapshot(name, data)


def test_compute_size_returns_key_count():
    _save("alpha", {"A": "1", "B": "2", "C": "3"})
    assert compute_size("alpha") == 3


def test_compute_size_empty_snapshot():
    _save("empty", {})
    assert compute_size("empty") == 0


def test_compute_size_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        compute_size("does_not_exist")


def test_get_size_returns_none_before_compute():
    _save("beta", {"X": "1"})
    assert get_size("beta") is None


def test_get_size_returns_cached_after_compute():
    _save("gamma", {"X": "1", "Y": "2"})
    compute_size("gamma")
    assert get_size("gamma") == 2


def test_compute_size_updates_cache_after_change():
    _save("delta", {"A": "1"})
    compute_size("delta")
    assert get_size("delta") == 1

    _save("delta", {"A": "1", "B": "2", "C": "3"})
    compute_size("delta")
    assert get_size("delta") == 3


def test_remove_size_clears_cache():
    _save("epsilon", {"K": "v"})
    compute_size("epsilon")
    assert get_size("epsilon") == 1
    remove_size("epsilon")
    assert get_size("epsilon") is None


def test_remove_size_nonexistent_is_safe():
    remove_size("ghost")  # should not raise


def test_list_sizes_returns_all_cached():
    _save("s1", {"A": "1"})
    _save("s2", {"A": "1", "B": "2", "C": "3"})
    _save("s3", {"A": "1", "B": "2"})
    compute_size("s1")
    compute_size("s2")
    compute_size("s3")
    sizes = list_sizes()
    assert set(sizes.keys()) == {"s1", "s2", "s3"}


def test_list_sizes_sorted_largest_first():
    _save("big", {"A": "1", "B": "2", "C": "3"})
    _save("small", {"X": "1"})
    compute_size("big")
    compute_size("small")
    sizes = list_sizes()
    keys = list(sizes.keys())
    assert keys.index("big") < keys.index("small")


def test_list_sizes_empty_when_none_computed():
    assert list_sizes() == {}
