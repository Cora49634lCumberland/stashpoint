"""Registration hook for the size CLI command group."""

from stashpoint.cli_snapshot_size import size_cmd


def register(cli):
    cli.add_command(size_cmd)
