"""Register namespace commands with the main CLI."""

from stashpoint.cli_namespace import namespace_cmd


def register(cli):
    cli.add_command(namespace_cmd)
