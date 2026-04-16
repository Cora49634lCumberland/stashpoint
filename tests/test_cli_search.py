import pytest
from click.testing import CliRunner
from stashpoint.cli_search import search_cmd
from stashpoint.storage import save_snapshot


@pytest.fixture(autouse=True)
def isolated_stash(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHPOINT_DIR", str(tmp_path))
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _make_snapshot(name, data):
    save_snapshot(name, data)


def test_search_run_key_match(runner):
    _make_snapshot("dev", {"DATABASE_URL": "postgres://", "PORT": "5432"})
    result = runner.invoke(search_cmd, ["run", "--key", "DATABASE*"])
    assert result.exit_code == 0
    assert "[dev]" in result.output
    assert "DATABASE_URL=postgres://" in result.output
    assert "PORT" not in result.output


def test_search_run_value_match(runner):
    _make_snapshot("prod", {"DB": "postgres://prod", "CACHE": "redis://"})
    result = runner.invoke(search_cmd, ["run", "--value", "postgres*"])
    assert result.exit_code == 0
    assert "DB=postgres://prod" in result.output


def test_search_run_no_results(runner):
    _make_snapshot("dev", {"PORT": "3000"})
    result = runner.invoke(search_cmd, ["run", "--key", "MISSING*"])
    assert result.exit_code == 0
    assert "No matches found." in result.output


def test_search_run_no_flags_errors(runner):
    result = runner.invoke(search_cmd, ["run"])
    assert result.exit_code != 0


def test_search_run_no_snapshots(runner):
    result = runner.invoke(search_cmd, ["run", "--key", "*"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output
