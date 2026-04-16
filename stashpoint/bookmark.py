"""Bookmark support: mark snapshots as favourites for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class BookmarkAlreadyExistsError(Exception):
    pass


class BookmarkNotFoundError(Exception):
    pass


def _get_bookmarks_path() -> Path:
    return get_stash_path() / "bookmarks.json"


def _load_bookmarks() -> List[str]:
    path = _get_bookmarks_path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_bookmarks(bookmarks: List[str]) -> None:
    _get_bookmarks_path().write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(name: str) -> List[str]:
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' does not exist.")
    bookmarks = _load_bookmarks()
    if name in bookmarks:
        raise BookmarkAlreadyExistsError(f"Snapshot '{name}' is already bookmarked.")
    bookmarks.append(name)
    _save_bookmarks(bookmarks)
    return bookmarks


def remove_bookmark(name: str) -> List[str]:
    bookmarks = _load_bookmarks()
    if name not in bookmarks:
        raise BookmarkNotFoundError(f"Snapshot '{name}' is not bookmarked.")
    bookmarks.remove(name)
    _save_bookmarks(bookmarks)
    return bookmarks


def list_bookmarks() -> List[str]:
    return _load_bookmarks()


def is_bookmarked(name: str) -> bool:
    return name in _load_bookmarks()
