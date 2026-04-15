"""Helper to register compare commands onto the main CLI.

Import and call `register(cli)` from cli.py to attach the compare group.
"""

from stashpoint.cli_compare import compare_cmd


def register(cli_group):
    """Attach the compare command group to *cli_group*.

    Parameters
    ----------
    cli_group:
        A Click ``Group`` instance (typically the root ``cli`` object)
        onto which the ``compare`` sub-command group will be mounted.

    Raises
    ------
    TypeError
        If *cli_group* does not expose an ``add_command`` method.
    """
    if not callable(getattr(cli_group, "add_command", None)):
        raise TypeError(
            f"cli_group must be a Click Group with an 'add_command' method, "
            f"got {type(cli_group).__name__!r} instead."
        )
    cli_group.add_command(compare_cmd)
