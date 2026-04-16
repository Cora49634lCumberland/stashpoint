"""Register watch commands with the main CLI."""

from stashpoint.cli_watch import watch_cmd


def register(cli):
    cli.add_command(watch_cmd)
