"""Registration helper for the checkpoint CLI group."""

from stashpoint.cli_checkpoint import checkpoint_cmd


def register(cli):
    cli.add_command(checkpoint_cmd)
