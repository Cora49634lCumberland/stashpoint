"""Register archive commands with the main CLI."""

from stashpoint.cli_archive import archive_cmd


def register(cli):
    cli.add_command(archive_cmd)
