import pytest
from pathlib import Path
from unittest.mock import patch
from stashpoint.schedule import (
    set_schedule,
    remove_schedule,
    get_schedule,
    list_schedules,
    SnapshotNotFoundError,
    ScheduleNotFoundError,
)


@pytest.fixture
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    return tmp_path


def _snapshots(*names):
    return {n: {} for n in names}


def test_set_schedule_returns_entry(isolated_stash):
    result = set_schedule("dev", "daily", snapshots=_snapshots("dev"))
    assert result["interval"] == "daily"


def test_set_schedule_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        set_schedule("ghost", "daily", snapshots={})


def test_set_schedule_invalid_interval_raises(isolated_stash):
    with pytest.raises(ValueError):
        set_schedule("dev", "minutely", snapshots=_snapshots("dev"))


def test_get_schedule_returns_none_when_not_set(isolated_stash):
    assert get_schedule("dev") is None


def test_get_schedule_returns_entry(isolated_stash):
    set_schedule("dev", "weekly", snapshots=_snapshots("dev"))
    assert get_schedule("dev") == {"interval": "weekly"}


def test_list_schedules_empty(isolated_stash):
    assert list_schedules() == {}


def test_list_schedules_multiple(isolated_stash):
    set_schedule("dev", "daily", snapshots=_snapshots("dev"))
    set_schedule("prod", "weekly", snapshots=_snapshots("prod"))
    data = list_schedules()
    assert "dev" in data and "prod" in data


def test_remove_schedule(isolated_stash):
    set_schedule("dev", "hourly", snapshots=_snapshots("dev"))
    remove_schedule("dev")
    assert get_schedule("dev") is None


def test_remove_missing_schedule_raises(isolated_stash):
    with pytest.raises(ScheduleNotFoundError):
        remove_schedule("nonexistent")


def test_set_schedule_overwrites(isolated_stash):
    set_schedule("dev", "daily", snapshots=_snapshots("dev"))
    set_schedule("dev", "hourly", snapshots=_snapshots("dev"))
    assert get_schedule("dev")["interval"] == "hourly"
