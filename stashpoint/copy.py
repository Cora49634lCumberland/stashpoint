"""Copy (duplicate) a snapshot under a new name."""

from stashpoint.storage import load_snapshot, save_snapshot


class SnapshotNotFoundError(Exception):
    """Raised when the source snapshot does not exist."""


class SnapshotAlreadyExistsError(Exception):
    """Raised when the destination snapshot name is already taken."""


def copy_snapshot(
    source: str,
    destination: str,
    *,
    overwrite: bool = False,
) -> dict:
    """Duplicate *source* snapshot as *destination*.

    Parameters
    ----------
    source:
        Name of the existing snapshot to copy.
    destination:
        Name for the new snapshot.
    overwrite:
        When *True* an existing *destination* snapshot is silently replaced.
        When *False* (default) a :class:`SnapshotAlreadyExistsError` is raised.

    Returns
    -------
    dict
        The env-var mapping that was copied.
    """
    data = load_snapshot(source)
    if data is None:
        raise SnapshotNotFoundError(f"Snapshot '{source}' does not exist.")

    existing = load_snapshot(destination)
    if existing is not None and not overwrite:
        raise SnapshotAlreadyExistsError(
            f"Snapshot '{destination}' already exists. "
            "Use --overwrite to replace it."
        )

    save_snapshot(destination, data)
    return data
