"""Register the annotation command group with the root CLI."""

from stashpoint.cli_annotation import annotation_cmd


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(annotation_cmd)
