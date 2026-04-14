"""Export and import snapshots to/from portable file formats."""

import json
import os
from pathlib import Path
from typing import Optional

from stashpoint.storage import load_snapshot, save_snapshot


def export_snapshot(name: str, output_path: Optional[str] = None) -> str:
    """Export a named snapshot to a JSON file.

    Args:
        name: The snapshot name to export.
        output_path: Optional file path to write to. Defaults to '<name>.stash.json'.

    Returns:
        The path of the written file.

    Raises:
        KeyError: If the snapshot does not exist.
    """
    snapshot = load_snapshot(name)
    if snapshot is None:
        raise KeyError(f"Snapshot '{name}' not found.")

    if output_path is None:
        output_path = f"{name}.stash.json"

    payload = {"name": name, "vars": snapshot}
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    return output_path


def import_snapshot(file_path: str, overwrite: bool = False) -> str:
    """Import a snapshot from a JSON file.

    Args:
        file_path: Path to a .stash.json file.
        overwrite: If False, raises ValueError when snapshot already exists.

    Returns:
        The name of the imported snapshot.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is invalid or snapshot exists and overwrite=False.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding="utf-8") as fh:
        try:
            payload = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid stash file format: {exc}") from exc

    if "name" not in payload or "vars" not in payload:
        raise ValueError("Stash file must contain 'name' and 'vars' keys.")

    name = payload["name"]
    vars_dict = payload["vars"]

    if not isinstance(vars_dict, dict):
        raise ValueError("'vars' must be a JSON object.")

    existing = load_snapshot(name)
    if existing is not None and not overwrite:
        raise ValueError(
            f"Snapshot '{name}' already exists. Use --overwrite to replace it."
        )

    save_snapshot(name, vars_dict)
    return name
