"""Helper to register compare commands onto the main CLI.

Import and call `register(cli)` from cli.py to attach the compare group.
"""

from stashpoint.cli_compare import compare_cmd


def register(cli_group):
    """Attach the compare command group to *cli_group*."""
    cli_group.add_command(compare_cmd)
