import json
from pathlib import Path
from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class FavoriteAlreadyExistsError(Exception):
    pass


class FavoriteNotFoundError(Exception):
    pass


def _get_favorites_path() -> Path:
    return get_stash_path() / "favorites.json"


def _load_favorites() -> list:
    path = _get_favorites_path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_favorites(favorites: list) -> None:
    path = _get_favorites_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(favorites, indent=2))


def add_favorite(name: str) -> list:
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(f"Snapshot '{name}' does not exist.")
    favorites = _load_favorites()
    if name in favorites:
        raise FavoriteAlreadyExistsError(f"'{name}' is already a favorite.")
    favorites.append(name)
    _save_favorites(favorites)
    return favorites


def remove_favorite(name: str) -> list:
    favorites = _load_favorites()
    if name not in favorites:
        raise FavoriteNotFoundError(f"'{name}' is not a favorite.")
    favorites.remove(name)
    _save_favorites(favorites)
    return favorites


def list_favorites() -> list:
    return _load_favorites()


def is_favorite(name: str) -> bool:
    return name in _load_favorites()
