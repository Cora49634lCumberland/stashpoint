import pytest
from stashpoint.archive import (
    archive_snapshot,
    unarchive_snapshot,
    list_archived,
    purge_snapshot,
    SnapshotNotFoundError,
    SnapshotAlreadyArchivedError,
    SnapshotNotArchivedError,
)
from stashpoint.storage import save_snapshot, load_snapshots


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


def _save(name, data):
    save_snapshot(name, data)


def test_archive_removes_from_active(isolated_stash):
    _save("dev", {"KEY": "val"})
    archive_snapshot("dev")
    assert "dev" not in load_snapshots()


def test_archive_appears_in_list(isolated_stash):
    _save("dev", {"KEY": "val"})
    archive_snapshot("dev")
    assert "dev" in list_archived()


def test_archive_missing_snapshot_raises(isolated_stash):
    with pytest.raises(SnapshotNotFoundError):
        archive_snapshot("ghost")


def test_archive_already_archived_raises(isolated_stash):
    _save("dev", {"KEY": "val"})
    archive_snapshot("dev")
    with pytest.raises(SnapshotAlreadyArchivedError):
        archive_snapshot("dev")


def test_unarchive_restores_to_active(isolated_stash):
    _save("dev", {"KEY": "val"})
    archive_snapshot("dev")
    unarchive_snapshot("dev")
    assert "dev" in load_snapshots()
    assert "dev" not in list_archived()


def test_unarchive_not_archived_raises(isolated_stash):
    with pytest.raises(SnapshotNotArchivedError):
        unarchive_snapshot("ghost")


def test_list_archived_empty(isolated_stash):
    assert list_archived() == []


def test_purge_removes_from_archive(isolated_stash):
    _save("dev", {"KEY": "val"})
    archive_snapshot("dev")
    purge_snapshot("dev")
    assert "dev" not in list_archived()


def test_purge_not_archived_raises(isolated_stash):
    with pytest.raises(SnapshotNotArchivedError):
        purge_snapshot("ghost")


def test_unarchive_preserves_data(isolated_stash):
    _save("dev", {"FOO": "bar", "BAZ": "qux"})
    archive_snapshot("dev")
    unarchive_snapshot("dev")
    assert load_snapshots()["dev"] == {"FOO": "bar", "BAZ": "qux"}
