"""Alias support: map short names to snapshot names."""

import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class AliasAlreadyExistsError(Exception):
    pass


class AliasNotFoundError(Exception):
    pass


def _get_aliases_path() -> Path:
    return get_stash_path() / "aliases.json"


def _load_aliases() -> dict:
    p = _get_aliases_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(aliases: dict) -> None:
    _get_aliases_path().write_text(json.dumps(aliases, indent=2))


def set_alias(alias: str, snapshot_name: str) -> str:
    """Create or overwrite an alias pointing to snapshot_name."""
    if load_snapshot(snapshot_name) is None:
        raise SnapshotNotFoundError(snapshot_name)
    aliases = _load_aliases()
    aliases[alias] = snapshot_name
    _save_aliases(aliases)
    return alias


def remove_alias(alias: str) -> None:
    aliases = _load_aliases()
    if alias not in aliases:
        raise AliasNotFoundError(alias)
    del aliases[alias]
    _save_aliases(aliases)


def resolve_alias(alias: str) -> str:
    """Return the snapshot name for the given alias."""
    aliases = _load_aliases()
    if alias not in aliases:
        raise AliasNotFoundError(alias)
    return aliases[alias]


def list_aliases() -> dict:
    return _load_aliases()
