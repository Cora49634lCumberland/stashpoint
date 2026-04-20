"""Tests for stashpoint.ttl."""

from __future__ import annotations

import os
from datetime import timedelta
from unittest.mock import patch

import pytest

from stashpoint.ttl import (
    InvalidTTLError,
    SnapshotNotFoundError,
    parse_ttl,
    set_ttl,
    get_ttl_remaining,
    remove_ttl,
)
from stashpoint import storage


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name: str, data: dict | None = None) -> None:
    storage.save_snapshot(name, data or {"KEY": "val"})


# ---------------------------------------------------------------------------
# parse_ttl
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ttl,expected_seconds", [
    ("30s", 30),
    ("5m", 300),
    ("2h", 7200),
    ("1d", 86400),
    ("1w", 604800),
    ("10M", 600),  # case-insensitive
])
def test_parse_ttl_valid(ttl, expected_seconds):
    result = parse_ttl(ttl)
    assert result == timedelta(seconds=expected_seconds)


@pytest.mark.parametrize("bad", ["abc", "10x", "", "1 h", "h1", "0.5h"])
def test_parse_ttl_invalid_raises(bad):
    with pytest.raises(InvalidTTLError):
        parse_ttl(bad)


# ---------------------------------------------------------------------------
# set_ttl
# ---------------------------------------------------------------------------

def test_set_ttl_returns_future_timestamp():
    _save("snap")
    import time
    before = time.time()
    ts = set_ttl("snap", "1h")
    after = time.time()
    assert ts > before + 3590  # roughly 1 hour ahead
    assert ts < after + 3610


def test_set_ttl_missing_snapshot_raises():
    with pytest.raises(SnapshotNotFoundError):
        set_ttl("ghost", "10m")


def test_set_ttl_invalid_ttl_raises():
    _save("snap")
    with pytest.raises(InvalidTTLError):
        set_ttl("snap", "bad")


# ---------------------------------------------------------------------------
# get_ttl_remaining
# ---------------------------------------------------------------------------

def test_get_ttl_remaining_returns_timedelta():
    _save("snap")
    set_ttl("snap", "2h")
    remaining = get_ttl_remaining("snap")
    assert remaining is not None
    assert timedelta(hours=1, minutes=59) < remaining <= timedelta(hours=2)


def test_get_ttl_remaining_none_when_not_set():
    _save("snap")
    assert get_ttl_remaining("snap") is None


def test_get_ttl_remaining_none_when_expired():
    _save("snap")
    import time
    # Set expiry in the past by directly calling set_expiry
    from stashpoint.expire import set_expiry
    set_expiry("snap", time.time() - 1)
    assert get_ttl_remaining("snap") is None


# ---------------------------------------------------------------------------
# remove_ttl
# ---------------------------------------------------------------------------

def test_remove_ttl_clears_expiry():
    _save("snap")
    set_ttl("snap", "30m")
    assert get_ttl_remaining("snap") is not None
    remove_ttl("snap")
    assert get_ttl_remaining("snap") is None
