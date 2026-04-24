"""Register dependency commands with the root CLI."""

from stashpoint.cli_dependency import dependency_cmd


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(dependency_cmd)
