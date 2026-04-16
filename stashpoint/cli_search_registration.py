"""Register search commands with the main CLI."""

from stashpoint.cli_search import search_cmd


def register(cli):
    """Attach search command group to the root CLI."""
    cli.add_command(search_cmd)
