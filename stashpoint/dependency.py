"""Snapshot dependency tracking — declare that one snapshot depends on another."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashpoint.storage import get_stash_path, load_snapshot


class SnapshotNotFoundError(Exception):
    pass


class DependencyAlreadyExistsError(Exception):
    pass


class DependencyNotFoundError(Exception):
    pass


class CircularDependencyError(Exception):
    pass


def _get_deps_path() -> Path:
    return get_stash_path() / "dependencies.json"


def _load_deps() -> dict:
    path = _get_deps_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_deps(data: dict) -> None:
    _get_deps_path().write_text(json.dumps(data, indent=2))


def _has_cycle(deps: dict, start: str, target: str) -> bool:
    """Return True if adding start -> target would create a cycle."""
    visited = set()
    queue = list(deps.get(target, []))
    while queue:
        node = queue.pop()
        if node == start:
            return True
        if node not in visited:
            visited.add(node)
            queue.extend(deps.get(node, []))
    return False


def add_dependency(name: str, depends_on: str) -> List[str]:
    """Declare that snapshot *name* depends on *depends_on*."""
    if load_snapshot(name) is None:
        raise SnapshotNotFoundError(name)
    if load_snapshot(depends_on) is None:
        raise SnapshotNotFoundError(depends_on)

    deps = _load_deps()
    current = deps.setdefault(name, [])

    if depends_on in current:
        raise DependencyAlreadyExistsError(depends_on)

    if _has_cycle(deps, name, depends_on):
        raise CircularDependencyError(
            f"Adding '{depends_on}' as dependency of '{name}' would create a cycle."
        )

    current.append(depends_on)
    _save_deps(deps)
    return list(current)


def remove_dependency(name: str, depends_on: str) -> List[str]:
    """Remove a declared dependency."""
    deps = _load_deps()
    current = deps.get(name, [])
    if depends_on not in current:
        raise DependencyNotFoundError(depends_on)
    current.remove(depends_on)
    deps[name] = current
    _save_deps(deps)
    return list(current)


def get_dependencies(name: str) -> List[str]:
    """Return direct dependencies of *name*."""
    return list(_load_deps().get(name, []))


def get_dependents(name: str) -> List[str]:
    """Return snapshots that directly depend on *name*."""
    return [k for k, v in _load_deps().items() if name in v]
