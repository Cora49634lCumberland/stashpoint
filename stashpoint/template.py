"""Template support: save a snapshot as a template and instantiate new snapshots from it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashpoint.storage import get_stash_path, load_snapshot, save_snapshot


class SnapshotNotFoundError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class TemplateAlreadyExistsError(Exception):
    pass


def _get_templates_path() -> Path:
    return get_stash_path().parent / "templates.json"


def _load_templates() -> dict[str, dict[str, str]]:
    path = _get_templates_path()
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_templates(templates: dict[str, dict[str, str]]) -> None:
    path = _get_templates_path()
    with path.open("w") as fh:
        json.dump(templates, fh, indent=2)


def save_as_template(snapshot_name: str, template_name: str) -> None:
    """Persist an existing snapshot as a named template."""
    data = load_snapshot(snapshot_name)
    if data is None:
        raise SnapshotNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    templates = _load_templates()
    if template_name in templates:
        raise TemplateAlreadyExistsError(f"Template '{template_name}' already exists.")
    templates[template_name] = data
    _save_templates(templates)


def instantiate_template(template_name: str, new_snapshot_name: str) -> dict[str, str]:
    """Create a new snapshot from a template."""
    templates = _load_templates()
    if template_name not in templates:
        raise TemplateNotFoundError(f"Template '{template_name}' not found.")
    data = dict(templates[template_name])
    save_snapshot(new_snapshot_name, data)
    return data


def list_templates() -> list[str]:
    """Return all template names sorted alphabetically."""
    return sorted(_load_templates().keys())


def delete_template(template_name: str) -> None:
    """Remove a template by name."""
    templates = _load_templates()
    if template_name not in templates:
        raise TemplateNotFoundError(f"Template '{template_name}' not found.")
    del templates[template_name]
    _save_templates(templates)
