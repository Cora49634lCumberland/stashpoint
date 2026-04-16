"""Clone a snapshot to a new name with optional key filtering."""

from stashpoint.storage import load_snapshot, save_snapshot


class SnapshotNotFoundError(Exception):
    pass


class SnapshotAlreadyExistsError(Exception):
    pass


def clone_snapshot(
    source: str,
    destination: str,
    keys: list[str] | None = None,
    overwrite: bool = False,
) -> dict:
    """Clone snapshot *source* to *destination*.

    Args:
        source: Name of the snapshot to clone.
        destination: Name for the new snapshot.
        keys: Optional list of keys to include. If None, all keys are copied.
        overwrite: If True, overwrite an existing destination snapshot.

    Returns:
        The cloned snapshot dict.
    """
    src = load_snapshot(source)
    if src is None:
        raise SnapshotNotFoundError(f"Snapshot '{source}' not found.")

    if not overwrite:
        existing = load_snapshot(destination)
        if existing is not None:
            raise SnapshotAlreadyExistsError(
                f"Snapshot '{destination}' already exists. Use --overwrite to replace it."
            )

    if keys is not None:
        cloned = {k: src[k] for k in keys if k in src}
    else:
        cloned = dict(src)

    save_snapshot(destination, cloned)
    return cloned
