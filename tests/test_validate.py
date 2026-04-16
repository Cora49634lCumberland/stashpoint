"""Tests for stashpoint.validate."""

import pytest
from unittest.mock import patch
from stashpoint.validate import validate_snapshot, SnapshotNotFoundError, ValidationResult


SAMPLE = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true", "PORT": "8080"}


def _patch(data):
    return patch("stashpoint.validate.load_snapshot", return_value=data)


def test_valid_when_all_required_present():
    with _patch(SAMPLE):
        result = validate_snapshot("prod", required=["DATABASE_URL", "PORT"])
    assert result.is_valid
    assert result.missing_keys == []
    assert result.forbidden_keys == []


def test_missing_required_key():
    with _patch(SAMPLE):
        result = validate_snapshot("prod", required=["SECRET_KEY"])
    assert not result.is_valid
    assert "SECRET_KEY" in result.missing_keys


def test_forbidden_key_present():
    with _patch(SAMPLE):
        result = validate_snapshot("prod", forbidden=["DEBUG"])
    assert not result.is_valid
    assert "DEBUG" in result.forbidden_keys


def test_forbidden_key_absent_is_valid():
    with _patch(SAMPLE):
        result = validate_snapshot("prod", forbidden=["SECRET_KEY"])
    assert result.is_valid


def test_combined_required_and_forbidden():
    with _patch(SAMPLE):
        result = validate_snapshot(
            "prod",
            required=["DATABASE_URL", "MISSING"],
            forbidden=["DEBUG"],
        )
    assert not result.is_valid
    assert "MISSING" in result.missing_keys
    assert "DEBUG" in result.forbidden_keys


def test_missing_snapshot_raises():
    with patch("stashpoint.validate.load_snapshot", return_value=None):
        with pytest.raises(SnapshotNotFoundError):
            validate_snapshot("ghost")


def test_no_rules_is_always_valid():
    with _patch(SAMPLE):
        result = validate_snapshot("prod")
    assert result.is_valid


def test_summary_contains_snapshot_name():
    with _patch(SAMPLE):
        result = validate_snapshot("prod", required=["MISSING"])
    assert "prod" in result.summary()
    assert "MISSING" in result.summary()


def test_summary_pass_message():
    with _patch(SAMPLE):
        result = validate_snapshot("prod")
    assert "passed" in result.summary()
