"""Tests for stashpoint.export — export/import snapshot functionality."""

import json
import os
import pytest
from pathlib import Path

from stashpoint.export import export_snapshot, import_snapshot
from stashpoint.storage import save_snapshot, load_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    """Redirect stash storage and working directory to a temp location."""
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    yield tmp_path


def test_export_creates_file(isolated_stash):
    save_snapshot("myproject", {"FOO": "bar", "PORT": "8080"})
    out = export_snapshot("myproject")
    assert Path(out).exists()
    assert out == "myproject.stash.json"


def test_export_file_contents(isolated_stash):
    save_snapshot("proj", {"KEY": "value"})
    out = export_snapshot("proj")
    with open(out) as fh:
        data = json.load(fh)
    assert data["name"] == "proj"
    assert data["vars"] == {"KEY": "value"}


def test_export_custom_output_path(isolated_stash, tmp_path):
    save_snapshot("snap", {"X": "1"})
    custom = str(tmp_path / "custom_output.json")
    out = export_snapshot("snap", output_path=custom)
    assert out == custom
    assert Path(custom).exists()


def test_export_missing_snapshot_raises(isolated_stash):
    with pytest.raises(KeyError, match="ghost"):
        export_snapshot("ghost")


def test_import_restores_snapshot(isolated_stash, tmp_path):
    file_path = tmp_path / "test.stash.json"
    file_path.write_text(json.dumps({"name": "imported", "vars": {"A": "1", "B": "2"}}))
    name = import_snapshot(str(file_path))
    assert name == "imported"
    assert load_snapshot("imported") == {"A": "1", "B": "2"}


def test_import_missing_file_raises(isolated_stash):
    with pytest.raises(FileNotFoundError):
        import_snapshot("/nonexistent/path/file.json")


def test_import_invalid_json_raises(isolated_stash, tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json{{")
    with pytest.raises(ValueError, match="Invalid stash file format"):
        import_snapshot(str(bad_file))


def test_import_missing_keys_raises(isolated_stash, tmp_path):
    bad_file = tmp_path / "incomplete.json"
    bad_file.write_text(json.dumps({"name": "oops"}))
    with pytest.raises(ValueError, match="'name' and 'vars'"):
        import_snapshot(str(bad_file))


def test_import_no_overwrite_raises(isolated_stash, tmp_path):
    save_snapshot("existing", {"OLD": "value"})
    file_path = tmp_path / "existing.stash.json"
    file_path.write_text(json.dumps({"name": "existing", "vars": {"NEW": "val"}}))
    with pytest.raises(ValueError, match="already exists"):
        import_snapshot(str(file_path), overwrite=False)


def test_import_overwrite_replaces_snapshot(isolated_stash, tmp_path):
    save_snapshot("existing", {"OLD": "value"})
    file_path = tmp_path / "existing.stash.json"
    file_path.write_text(json.dumps({"name": "existing", "vars": {"NEW": "val"}}))
    import_snapshot(str(file_path), overwrite=True)
    assert load_snapshot("existing") == {"NEW": "val"}
